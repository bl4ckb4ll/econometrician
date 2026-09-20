{-# LANGUAGE ScopedTypeVariables #-}

-- Dependency-free TSV frontend and numerical kernel for the caster receipt.
-- A nominal-model estimate is allowed without an error bar; a statistical
-- standard deviation is not.

module Main where

import Control.Monad (forM, forM_, unless, when)
import Data.List (elemIndex, intercalate, nub, sort, subsequences)
import qualified Data.Map.Strict as Map
import Data.Maybe (fromMaybe)
import System.Directory (doesFileExist)
import System.Environment (getArgs)
import System.Exit (exitFailure)
import System.FilePath ((</>))
import System.IO (hPutStrLn, stderr)
import Text.Printf (printf)
import Text.Read (readMaybe)

type Row = Map.Map String String
type Matrix = [[Double]]

inputLabels :: [String]
inputLabels =
  [ "theta_right_deg", "theta_left_deg"
  , "gamma_right_deg", "gamma_left_deg"
  ]

radPerDeg :: Double
radPerDeg = pi / 180.0

failContract :: String -> String -> IO a
failContract code detail = do
  hPutStrLn stderr (intercalate "\t" ["FAIL", code, detail])
  exitFailure

require :: Bool -> String -> String -> IO ()
require condition code detail = unless condition (failContract code detail)

splitTab :: String -> [String]
splitTab value =
  case break (== '\t') value of
    (first, []) -> [first]
    (first, _ : rest) -> first : splitTab rest

readTsv :: FilePath -> IO ([String], [Row])
readTsv path = do
  exists <- doesFileExist path
  require exists "missing_input" path
  content <- readFile path
  case lines content of
    [] -> failContract "empty_tsv" path
    headerLine : bodyLines -> do
      let header = splitTab headerLine
      parsed <- forM (zip [2 :: Int ..] bodyLines) $ \(lineNumber, line) -> do
        let values = splitTab line
        require (length values == length header) "invalid_tsv_width"
          (path ++ ":" ++ show lineNumber)
        pure (Map.fromList (zip header values))
      pure (header, parsed)

field :: Row -> String -> String
field row name = fromMaybe (error ("validated TSV lacks field " ++ name))
                           (Map.lookup name row)

parseNumber :: String -> String -> IO Double
parseNumber label text =
  case readMaybe text of
    Just value | not (isNaN value) && not (isInfinite value) -> pure value
    _ -> failContract "invalid_number" label

formatNumber :: Double -> String
formatNumber value = printf "%.12f" value

emit :: String -> String -> IO ()
emit key value = putStrLn (key ++ "\t" ++ value)

signedCoefficient :: [Double] -> Double
signedCoefficient [thetaRight, thetaLeft, gammaRight, gammaLeft] =
  let denominator = sin (thetaRight * radPerDeg) - sin (thetaLeft * radPerDeg)
  in (gammaRight - gammaLeft) / denominator
signedCoefficient _ = error "four inputs required"

casterMagnitude :: [Double] -> Double
casterMagnitude = abs . signedCoefficient

analyticJacobian :: [Double] -> [Double]
analyticJacobian [thetaRight, thetaLeft, gammaRight, gammaLeft] =
  let tr = thetaRight * radPerDeg
      tl = thetaLeft * radPerDeg
      numerator = gammaRight - gammaLeft
      denominator = sin tr - sin tl
      signed = numerator / denominator
      direction = if signed > 0 then 1.0 else -1.0
  in [ direction * ((-numerator * cos tr) / denominator ^ (2 :: Int)) * radPerDeg
     , direction * (( numerator * cos tl) / denominator ^ (2 :: Int)) * radPerDeg
     , direction / denominator
     , -direction / denominator
     ]
analyticJacobian _ = error "four inputs required"

replaceAt :: Int -> Double -> [Double] -> [Double]
replaceAt index value values =
  take index values ++ [value] ++ drop (index + 1) values

finiteDifferenceJacobian :: [Double] -> [Double]
finiteDifferenceJacobian inputs =
  let steps = [1e-5, 1e-5, 1e-6, 1e-6]
      one index step =
        let original = inputs !! index
            plus = replaceAt index (original + step) inputs
            minus = replaceAt index (original - step) inputs
        in (casterMagnitude plus - casterMagnitude minus) / (2 * step)
  in zipWith one [0 ..] steps

validatePair :: [String] -> [Row] -> IO ([Double], Row, Row)
validatePair header rows = do
  let expected =
        [ "observation_id", "endpoint", "generation", "adjustment_state", "side"
        , "sweep_id", "approach_direction", "theta_deg", "gamma_deg"
        , "theta_source_id", "theta_source_kind"
        ]
  require (header == expected) "invalid_observation_header" (intercalate "," header)
  let rights = filter ((== "right") . (`field` "endpoint")) rows
      lefts = filter ((== "left") . (`field` "endpoint")) rows
  require (length rows == 2 && length rights == 1 && length lefts == 1)
    "pair_requires_one_right_and_one_left_endpoint" ""
  require (length (nub (map (`field` "observation_id") rows)) == 2)
    "duplicate_observation_id" ""
  let matchFields =
        [ "generation", "adjustment_state", "side", "sweep_id"
        , "approach_direction", "theta_source_id", "theta_source_kind"
        ]
  forM_ matchFields $ \name -> do
    let values = map (`field` name) rows
    require (all (not . null) values && length (nub values) == 1)
      "incompatible_observation_provenance" name
  let right = head rights
      left = head lefts
  tr <- parseNumber "right.theta_deg" (field right "theta_deg")
  tl <- parseNumber "left.theta_deg" (field left "theta_deg")
  gr <- parseNumber "right.gamma_deg" (field right "gamma_deg")
  gl <- parseNumber "left.gamma_deg" (field left "gamma_deg")
  let inputs = [tr, tl, gr, gl]
      denominator = sin (tr * radPerDeg) - sin (tl * radPerDeg)
  require (abs denominator >= 1e-15) "zero_steering_denominator" ""
  require (gr /= gl) "magnitude_not_differentiable_at_zero" ""
  pure (inputs, right, left)

readPolicy :: FilePath -> IO (Map.Map String String)
readPolicy path = do
  (header, rows) <- readTsv path
  require (header == ["key", "value"]) "invalid_policy_header"
    (intercalate "," header)
  let keys = map (`field` "key") rows
  require (length keys == length (nub keys)) "duplicate_policy_key" ""
  pure (Map.fromList [(field row "key", field row "value") | row <- rows])

policyValue :: Map.Map String String -> String -> IO String
policyValue policy key =
  case Map.lookup key policy of
    Nothing -> failContract "missing_policy_key" key
    Just value -> pure value

splitSemicolon :: String -> [String]
splitSemicolon "" = []
splitSemicolon value =
  case break (== ';') value of
    (first, []) -> [first]
    (first, _ : rest) -> first : splitSemicolon rest

determinant :: Matrix -> Double
determinant [] = 1.0
determinant [[value]] = value
determinant matrix =
  let firstRow = head matrix
      minor column = map (removeAt column) (tail matrix)
      term column value =
        (if even column then 1.0 else -1.0) * value * determinant (minor column)
  in sum (zipWith term [0 ..] firstRow)
  where
    removeAt index values = take index values ++ drop (index + 1) values

principalSubmatrix :: Matrix -> [Int] -> Matrix
principalSubmatrix matrix indices =
  [[matrix !! row !! column | column <- indices] | row <- indices]

isPositiveSemidefinite :: Matrix -> Bool
isPositiveSemidefinite matrix =
  let indices = filter (not . null) (subsequences [0, 1, 2, 3])
  in all (>= (-1e-10))
       [determinant (principalSubmatrix matrix selected) | selected <- indices]

quadraticForm :: [Double] -> Matrix -> Double
quadraticForm vector matrix =
  sum [vector !! row * matrix !! row !! column * vector !! column
      | row <- [0 .. 3], column <- [0 .. 3]]

data CovarianceReceipt = CovarianceReceipt
  { covarianceStatus :: String
  , covarianceSourceIds :: [String]
  , covarianceEffects :: [String]
  , covarianceContributions :: [(String, Double)]
  , covarianceVariance :: Double
  }

readCovarianceSources
  :: FilePath -> Map.Map String String -> [Double] -> IO (Maybe CovarianceReceipt)
readCovarianceSources caseDir policy jacobian = do
  let sourcesPath = caseDir </> "sources.tsv"
      cellsPath = caseDir </> "covariance.tsv"
  hasSources <- doesFileExist sourcesPath
  hasCells <- doesFileExist cellsPath
  if not hasSources && not hasCells
    then pure Nothing
    else do
      require (hasSources && hasCells)
        "sources_and_covariance_must_be_supplied_together" ""
      (sourceHeader, sources) <- readTsv sourcesPath
      (cellHeader, cells) <- readTsv cellsPath
      require (sourceHeader ==
        ["source_id", "kind", "covered_effects", "provenance", "empirical_status"])
        "invalid_sources_header" ""
      require (cellHeader == ["source_id", "row_label", "column_label", "value"])
        "invalid_covariance_header" ""
      let sourceIds = map (`field` "source_id") sources
          cellSourceIds = nub (map (`field` "source_id") cells)
          allowedKinds =
            [ "measurement_repeatability", "instrument_resolution", "steering_angle"
            , "calibration_shared", "between_pair", "between_session", "model"
            , "joint_covariance", "shared_systematic"
            ]
      require (not (null sources) && all (not . null) sourceIds &&
               length sourceIds == length (nub sourceIds))
        "invalid_or_duplicate_source_id" ""
      require (all ((`elem` allowedKinds) . (`field` "kind")) sources)
        "unknown_error_source_kind" ""
      require (sort sourceIds == sort cellSourceIds)
        "covariance_source_identity_mismatch" ""
      independence <- policyValue policy "independence_assertion"
      when (length sources > 1) $
        require (not (null independence)) "missing_independence_assertion" ""

      let effectLists = map (splitSemicolon . (`field` "covered_effects")) sources
          allEffects = concat effectLists
      require (length allEffects == length (nub allEffects))
        "double_counted_uncertainty" ""

      contributions <- forM sources $ \source -> do
        let sourceId = field source "source_id"
            sourceCells = filter ((== sourceId) . (`field` "source_id")) cells
            actualKeys = sort [(field row "row_label", field row "column_label")
                              | row <- sourceCells]
            expectedKeys = sort [(row, column) | row <- inputLabels, column <- inputLabels]
        require (length sourceCells == 16 && actualKeys == expectedKeys)
          "covariance_must_name_all_16_cells_once" sourceId
        matrix <- forM inputLabels $ \rowLabel ->
          forM inputLabels $ \columnLabel -> do
            let matches = filter (\row -> field row "row_label" == rowLabel &&
                                          field row "column_label" == columnLabel)
                                 sourceCells
            parseNumber (sourceId ++ "." ++ rowLabel ++ "." ++ columnLabel)
                        (field (head matches) "value")
        let symmetric = and [abs (matrix !! row !! column - matrix !! column !! row) <= 1e-12
                            | row <- [0 .. 3], column <- [0 .. 3]]
        require symmetric "covariance_not_symmetric" sourceId
        require (isPositiveSemidefinite matrix)
          "covariance_not_positive_semidefinite" sourceId
        pure (sourceId, quadraticForm jacobian matrix)
      let totalVariance = sum (map snd contributions)
          empirical = all ((== "empirical") . (`field` "empirical_status")) sources
          status = if empirical then "probabilistic_standard_error"
                                else "illustrative_only_not_error_bar"
      require (totalVariance >= (-1e-10)) "negative_propagated_variance" ""
      pure (Just (CovarianceReceipt status sourceIds allEffects contributions
              (max 0 totalVariance)))

data BoundsReceipt = BoundsReceipt
  { boundsKind :: String
  , linearLower :: Double
  , linearUpper :: Double
  , nonlinearLower :: Double
  , nonlinearUpper :: Double
  , nonlinearMinus :: Double
  , nonlinearPlus :: Double
  }

readBounds :: FilePath -> [Double] -> [Double] -> IO (Maybe BoundsReceipt)
readBounds path center jacobian = do
  exists <- doesFileExist path
  if not exists
    then pure Nothing
    else do
      (header, rows) <- readTsv path
      require (header == ["input_label", "radius", "source_kind", "provenance"])
        "invalid_bounds_header" ""
      let labels = map (`field` "input_label") rows
      require (length rows == 4 && sort labels == sort inputLabels &&
               length labels == length (nub labels))
        "bounds_must_name_all_four_inputs_once" ""
      radii <- forM inputLabels $ \label -> do
        let row = head (filter ((== label) . (`field` "input_label")) rows)
        radius <- parseNumber ("radius." ++ label) (field row "radius")
        require (radius >= 0) "negative_bound_radius" label
        pure radius
      let linearRadius = sum (zipWith (\j r -> abs j * r) jacobian radii)
          centerOutput = casterMagnitude center
          thetaRightRange = [center !! 0 - radii !! 0, center !! 0 + radii !! 0]
          thetaLeftRange = [center !! 1 - radii !! 1, center !! 1 + radii !! 1]
      require (minimum (thetaRightRange ++ thetaLeftRange) >= (-90) &&
               maximum (thetaRightRange ++ thetaLeftRange) <= 90)
        "nonlinear_box_requires_monotone_sine_angle_ranges" ""
      let denominatorRange = sort
            [ sin (head thetaRightRange * radPerDeg) - sin (last thetaLeftRange * radPerDeg)
            , sin (last thetaRightRange * radPerDeg) - sin (head thetaLeftRange * radPerDeg)
            ]
      require (not (head denominatorRange <= 0 && last denominatorRange >= 0))
        "nonlinear_box_contains_steering_singularity" ""
      let numeratorCenter = center !! 2 - center !! 3
          numeratorRadius = radii !! 2 + radii !! 3
          numeratorRange = [numeratorCenter - numeratorRadius, numeratorCenter + numeratorRadius]
          candidates = [abs (numerator / denominator)
                       | numerator <- numeratorRange, denominator <- denominatorRange]
          lower = if head numeratorRange <= 0 && last numeratorRange >= 0
                    then 0 else minimum candidates
          upper = maximum candidates
          kind = intercalate ";" (nub (map (`field` "source_kind") rows))
      pure (Just (BoundsReceipt kind
              (centerOutput - linearRadius) (centerOutput + linearRadius)
              lower upper (centerOutput - lower) (upper - centerOutput)))

data ResamplingReceipt = ResamplingReceipt String Int

auditResampling
  :: Maybe FilePath -> [String] -> IO (Maybe ResamplingReceipt)
auditResampling Nothing _ = pure Nothing
auditResampling (Just path) explicitEffects = do
  (header, rows) <- readTsv path
  require (header ==
    ["sampling_structure", "resampling_unit", "group_id", "covered_effects", "provenance"])
    "invalid_resampling_header" ""
  let structures = nub (map (`field` "sampling_structure") rows)
      units = nub (map (`field` "resampling_unit") rows)
  require (length structures == 1 && length units == 1)
    "inconsistent_resampling_plan" ""
  let structure = head structures
      unit = head units
  when (structure == "designed" && unit == "steering_position") $
    failContract "designed_positions_not_iid" ""
  let effects = nub (concatMap (splitSemicolon . (`field` "covered_effects")) rows)
      overlap = filter (`elem` explicitEffects) effects
  require (null overlap) "bootstrap_measurement_error_double_count"
    (intercalate ";" overlap)
  let groupCount = length (nub (map (`field` "group_id") rows))
  require (groupCount >= 2) "fewer_than_two_resampling_groups" ""
  pure (Just (ResamplingReceipt unit groupCount))

main :: IO ()
main = do
  arguments <- getArgs
  (caseDir, requestedResampling) <- case arguments of
    [directory] -> pure (directory, Nothing)
    [directory, "--resampling", path] -> pure (directory, Just path)
    _ -> failContract "usage" "CasterReceipt.hs CASE_DIR [--resampling FILE]"
  policy <- readPolicy (caseDir </> "policy.tsv")
  (observationHeader, observations) <- readTsv (caseDir </> "observations.tsv")
  (inputs, right, left) <- validatePair observationHeader observations
  let jacobian = analyticJacobian inputs
      numerical = finiteDifferenceJacobian inputs
      derivativeError = maximum (zipWith (\a b -> abs (a - b)) jacobian numerical)
  require (derivativeError <= 1e-8) "finite_difference_jacobian_mismatch" ""
  covariance <- readCovarianceSources caseDir policy jacobian
  bounds <- readBounds (caseDir </> "bounds.tsv") inputs jacobian
  defaultResamplingExists <- doesFileExist (caseDir </> "resampling.tsv")
  let resamplingPath = case requestedResampling of
        Just path -> Just path
        Nothing -> if defaultResamplingExists then Just (caseDir </> "resampling.tsv") else Nothing
      effects = maybe [] covarianceEffects covariance
  resampling <- auditResampling resamplingPath effects
  caseId <- policyValue policy "case_id"
  estimateKind <- policyValue policy "estimate_kind"
  unresolved <- policyValue policy "unresolved_effects"

  emit "receipt_version" "caster-uncertainty-v1"
  emit "implementation" "Haskell"
  emit "case_id" caseId
  emit "status" "PASS"
  emit "estimate_kind" estimateKind
  emit "generation" (field right "generation")
  emit "adjustment_state" (field right "adjustment_state")
  emit "side" (field right "side")
  emit "sweep_id" (field right "sweep_id")
  emit "approach_direction" (field right "approach_direction")
  emit "right_observation_id" (field right "observation_id")
  emit "left_observation_id" (field left "observation_id")
  emit "theta_source_id" (field right "theta_source_id")
  emit "theta_source_kind" (field right "theta_source_kind")
  emit "input_order" (intercalate "," inputLabels)
  emit "input_values" (intercalate "," (map formatNumber inputs))
  emit "signed_coefficient_deg" (formatNumber (signedCoefficient inputs))
  emit "caster_magnitude_deg" (formatNumber (casterMagnitude inputs))
  emit "jacobian_values" (intercalate "," (map formatNumber jacobian))
  emit "jacobian_units" "deg_per_deg,deg_per_deg,deg_per_deg,deg_per_deg"
  emit "finite_difference_max_abs_error" (formatNumber derivativeError)
  emit "unresolved_effects" unresolved
  case covariance of
    Nothing -> do
      emit "covariance_status" "not_supplied"
      emit "error_bar_status" "not_computed"
    Just receipt -> do
      emit "covariance_status" (covarianceStatus receipt)
      emit "covariance_source_ids" (intercalate ";" (covarianceSourceIds receipt))
      emit "propagated_variance_deg2" (formatNumber (covarianceVariance receipt))
      emit "propagated_standard_deviation_deg"
        (formatNumber (sqrt (covarianceVariance receipt)))
      forM_ (covarianceContributions receipt) $ \(sourceId, contribution) ->
        emit ("variance_contribution." ++ sourceId) (formatNumber contribution)
      emit "error_bar_status" (covarianceStatus receipt)
  case bounds of
    Nothing -> emit "bounds_status" "not_supplied"
    Just receipt -> do
      emit "bounds_status" (boundsKind receipt)
      emit "bounds_coverage" "complete_box_interval"
      emit "linear_interval_deg" (intercalate ","
        [formatNumber (linearLower receipt), formatNumber (linearUpper receipt)])
      emit "nonlinear_interval_deg" (intercalate ","
        [formatNumber (nonlinearLower receipt), formatNumber (nonlinearUpper receipt)])
      emit "nonlinear_minus_plus_deg" (intercalate ","
        [formatNumber (nonlinearMinus receipt), formatNumber (nonlinearPlus receipt)])
  case resampling of
    Nothing -> emit "resampling_status" "not_requested"
    Just (ResamplingReceipt unit count) -> do
      emit "resampling_status" "plan_validated_not_executed"
      emit "resampling_unit" unit
      emit "independent_group_count" (show count)
  -- Analytically soluble regression: independent variance 0.25 on each of
  -- three estimates plus one shared variance 1.0.
  emit "three_pair_correlated_variance" (formatNumber (1.0 + 0.25 / 3.0))
  emit "three_pair_naive_variance" (formatNumber ((1.0 + 0.25) / 3.0))
