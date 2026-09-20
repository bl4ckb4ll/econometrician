module CasterReceipt where

-- Typed numerical acceptance kernel for the same fixture consumed by the R
-- and Haskell TSV frontends.  Keeping file ingestion out of this kernel makes
-- its boundary explicit: it independently evaluates the formula, Jacobian,
-- covariance, nonlinear interval, shared modes, and resampling decisions.

open import Agda.Builtin.Bool using (Bool; true; false)
open import Agda.Builtin.Float
  using (Float)
  renaming
    ( primFloatPlus to infixl 6 _+_
    ; primFloatMinus to infixl 6 _-_
    ; primFloatTimes to infixl 7 _*_
    ; primFloatDiv to infixl 7 _÷_
    ; primFloatNegate to infix 9 -_
    ; primFloatSin to sin
    ; primFloatCos to cos
    ; primFloatSqrt to sqrt
    ; primFloatLess to _<_
    ; primShowFloat to showFloat
    )
open import Agda.Builtin.IO using (IO)
open import Agda.Builtin.Nat using (Nat; suc)
open import Agda.Builtin.String
  using (String)
  renaming (primStringAppend to _++_)
open import Agda.Builtin.Unit using (⊤)

postulate
  putStrLn : String → IO ⊤
  _>>_ : {A B : Set} → IO A → IO B → IO B

infixr 1 _>>_

{-# FOREIGN GHC import qualified Data.Text.IO as Text #-}
{-# COMPILE GHC putStrLn = Text.putStrLn #-}
{-# COMPILE GHC _>>_ = \ _ _ -> (>>) #-}

not : Bool → Bool
not true = false
not false = true

_and_ : Bool → Bool → Bool
true and right = right
false and _ = false

infixr 2 _and_

absolute : Float → Float
absolute value with value < 0.0
... | true = - value
... | false = value

directionOf : Float → Float
directionOf value with value < 0.0
... | true = -1.0
... | false = 1.0

within : Float → Float → Float → Bool
within actual expected tolerance = absolute (actual - expected) < tolerance

radPerDegree : Float
radPerDegree = 3.141592653589793 ÷ 180.0

sineDegrees : Float → Float
sineDegrees angle = sin (angle * radPerDegree)

cosineDegrees : Float → Float
cosineDegrees angle = cos (angle * radPerDegree)

record PairInput : Set where
  constructor pair
  field
    thetaRight : Float
    thetaLeft : Float
    gammaRight : Float
    gammaLeft : Float

open PairInput

denominator : PairInput → Float
denominator input =
  sineDegrees (thetaRight input) - sineDegrees (thetaLeft input)

numerator : PairInput → Float
numerator input = gammaRight input - gammaLeft input

signedCoefficient : PairInput → Float
signedCoefficient input = numerator input ÷ denominator input

casterMagnitude : PairInput → Float
casterMagnitude input = absolute (signedCoefficient input)

record Jacobian : Set where
  constructor jacobian
  field
    dThetaRight : Float
    dThetaLeft : Float
    dGammaRight : Float
    dGammaLeft : Float

open Jacobian

analyticJacobian : PairInput → Jacobian
analyticJacobian input =
  let n = numerator input
      d = denominator input
      direction = directionOf (n ÷ d)
      squared = d * d
  in jacobian
       (direction * ((- n * cosineDegrees (thetaRight input)) ÷ squared) * radPerDegree)
       (direction * ((n * cosineDegrees (thetaLeft input)) ÷ squared) * radPerDegree)
       (direction ÷ d)
       (- direction ÷ d)

finiteDifferenceThetaRight : PairInput → Float → Float
finiteDifferenceThetaRight input step =
  let plus = pair
        (thetaRight input + step) (thetaLeft input)
        (gammaRight input) (gammaLeft input)
      minus = pair
        (thetaRight input - step) (thetaLeft input)
        (gammaRight input) (gammaLeft input)
  in (casterMagnitude plus - casterMagnitude minus) ÷ (2.0 * step)

record DiagonalCovariance : Set where
  constructor diagonalCovariance
  field
    varianceThetaRight : Float
    varianceThetaLeft : Float
    varianceGammaRight : Float
    varianceGammaLeft : Float

open DiagonalCovariance

propagateDiagonal : Jacobian → DiagonalCovariance → Float
propagateDiagonal derivative covariance =
    dThetaRight derivative * dThetaRight derivative * varianceThetaRight covariance
  + dThetaLeft derivative * dThetaLeft derivative * varianceThetaLeft covariance
  + dGammaRight derivative * dGammaRight derivative * varianceGammaRight covariance
  + dGammaLeft derivative * dGammaLeft derivative * varianceGammaLeft covariance

record NonlinearInterval : Set where
  constructor nonlinearInterval
  field
    lower : Float
    upper : Float

open NonlinearInterval

symmetricAngleBox : Float → Float → Float → NonlinearInterval
symmetricAngleBox theta radius gammaDifference =
  nonlinearInterval
    (absolute (gammaDifference ÷ (2.0 * sineDegrees (theta + radius))))
    (absolute (gammaDifference ÷ (2.0 * sineDegrees (theta - radius))))

data SamplingStructure : Set where
  designed clustered : SamplingStructure

data ResamplingUnit : Set where
  steeringPosition sweep session : ResamplingUnit

planIsValid : SamplingStructure → ResamplingUnit → Nat → Bool → Bool
planIsValid designed steeringPosition _ _ = false
planIsValid _ _ 0 _ = false
planIsValid _ _ (suc 0) _ = false
planIsValid _ _ _ true = false
planIsValid _ _ _ false = true

g2Input : PairInput
g2Input = pair (180.0 ÷ 17.4) (- (180.0 ÷ 17.4)) 0.5 2.5

g2Estimate : Float
g2Estimate = casterMagnitude g2Input

g2Jacobian : Jacobian
g2Jacobian = analyticJacobian g2Input

g2Stress : NonlinearInterval
g2Stress = symmetricAngleBox (180.0 ÷ 17.4) 5.0 (0.5 - 2.5)

g2LinearRadius : Float
g2LinearRadius =
  absolute (dThetaRight g2Jacobian) * 5.0
  + absolute (dThetaLeft g2Jacobian) * 5.0

commonSteeringZeroLoading : Float
commonSteeringZeroLoading =
  dThetaRight g2Jacobian + dThetaLeft g2Jacobian

commonCamberZeroLoading : Float
commonCamberZeroLoading =
  dGammaRight g2Jacobian + dGammaLeft g2Jacobian

h006Input : PairInput
h006Input = pair 22.5 (- 22.5) 3.75 0.0

h006Variance : Float
h006Variance = propagateDiagonal
  (analyticJacobian h006Input)
  (diagonalCovariance 25.0 25.0 0.0625 0.0625)

correlatedThreePairVariance : Float
correlatedThreePairVariance = 1.0 + (0.25 ÷ 3.0)

naiveThreePairVariance : Float
naiveThreePairVariance = (1.0 + 0.25) ÷ 3.0

checksPass : Bool
checksPass =
  within g2Estimate 5.568798743106686 0.0000000001
  and within (dThetaRight g2Jacobian) (- 0.2662274831764701) 0.0000000001
  and within (dThetaLeft g2Jacobian) 0.2662274831764701 0.0000000001
  and within (dGammaRight g2Jacobian) (- 2.784399371553343) 0.0000000001
  and within (dGammaLeft g2Jacobian) 2.784399371553343 0.0000000001
  and within
    (finiteDifferenceThetaRight g2Input 0.00001)
    (dThetaRight g2Jacobian) 0.00000001
  and within (lower g2Stress) 3.778894920165921 0.0000000001
  and within (upper g2Stress) 10.735418793944593 0.0000000001
  and within (sqrt h006Variance) 0.863804278906 0.0000000001
  and within commonSteeringZeroLoading 0.0 0.0000000001
  and within commonCamberZeroLoading 0.0 0.0000000001
  and (naiveThreePairVariance < correlatedThreePairVariance)
  and not (planIsValid designed steeringPosition 7 false)
  and not (planIsValid clustered sweep 2 true)

statusText : Bool → String
statusText true = "PASS"
statusText false = "FAIL"

main : IO ⊤
main =
  putStrLn "receipt_version\tcaster-uncertainty-v1" >>
  putStrLn "implementation\tAgda" >>
  putStrLn ("status\t" ++ statusText checksPass) >>
  putStrLn "case_id\tg2-passenger-half-turn" >>
  putStrLn "theta_source_kind\tmanual_17.4_to_1_nominal_conversion" >>
  putStrLn ("caster_magnitude_deg\t" ++ showFloat g2Estimate) >>
  putStrLn ("jacobian.theta_right_deg\t" ++ showFloat (dThetaRight g2Jacobian)) >>
  putStrLn ("jacobian.theta_left_deg\t" ++ showFloat (dThetaLeft g2Jacobian)) >>
  putStrLn ("jacobian.gamma_right_deg\t" ++ showFloat (dGammaRight g2Jacobian)) >>
  putStrLn ("jacobian.gamma_left_deg\t" ++ showFloat (dGammaLeft g2Jacobian)) >>
  putStrLn "error_bar_status\tnot_computed" >>
  putStrLn "bounds_status\thistorical_stress_test_not_measurement_uncertainty" >>
  putStrLn
    ("linear_interval_deg\t"
      ++ showFloat (g2Estimate - g2LinearRadius)
      ++ "," ++ showFloat (g2Estimate + g2LinearRadius)) >>
  putStrLn
    ("nonlinear_interval_deg\t"
      ++ showFloat (lower g2Stress)
      ++ "," ++ showFloat (upper g2Stress)) >>
  putStrLn
    ("h006_propagated_standard_deviation_deg\t" ++ showFloat (sqrt h006Variance)) >>
  putStrLn "h006_error_bar_status\tillustrative_only_not_error_bar" >>
  putStrLn
    ("three_pair_correlated_variance\t" ++ showFloat correlatedThreePairVariance) >>
  putStrLn
    ("three_pair_naive_variance\t" ++ showFloat naiveThreePairVariance) >>
  putStrLn "designed_steering_positions_bootstrap\tREJECTED" >>
  putStrLn "bootstrap_explicit_error_overlap\tREJECTED"
