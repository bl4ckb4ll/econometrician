#!/usr/bin/env Rscript

# A dependency-free, file-driven regression/reference receipt.
# R's numeric carrier is binary64, so this executable is not the physical
# measurement path. It remains an independent oracle for formula, covariance,
# bounds, provenance, and resampling safeguards.

input_labels <- c(
  "theta_right_deg", "theta_left_deg",
  "gamma_right_deg", "gamma_left_deg"
)
rad_per_deg <- pi / 180

abort_contract <- function(code, detail = "") {
  message(paste("FAIL", code, detail, sep = "\t"))
  quit(status = 2)
}

read_tsv <- function(path) {
  if (!file.exists(path)) abort_contract("missing_input", path)
  read.delim(
    path, header = TRUE, sep = "\t", quote = "", comment.char = "",
    stringsAsFactors = FALSE, check.names = FALSE,
    colClasses = "character"
  )
}

read_policy <- function(path) {
  rows <- read_tsv(path)
  if (!identical(names(rows), c("key", "value"))) {
    abort_contract("invalid_policy_header", paste(names(rows), collapse = ","))
  }
  if (anyDuplicated(rows$key)) abort_contract("duplicate_policy_key")
  setNames(rows$value, rows$key)
}

number <- function(text, field) {
  value <- suppressWarnings(as.numeric(text))
  if (length(value) != 1 || !is.finite(value)) {
    abort_contract("invalid_number", field)
  }
  value
}

format_number <- function(value) sprintf("%.12f", value)

emit <- function(key, value) cat(key, as.character(value), sep = "\t", fill = TRUE)

signed_coefficient <- function(x) {
  denominator <- sin(x[1] * rad_per_deg) - sin(x[2] * rad_per_deg)
  if (abs(denominator) < 1e-15) abort_contract("zero_steering_denominator")
  (x[3] - x[4]) / denominator
}

caster_magnitude <- function(x) abs(signed_coefficient(x))

odd_even_components <- function(gamma_plus, gamma_minus) {
  c(
    odd = (gamma_plus - gamma_minus) / 2,
    even = (gamma_plus + gamma_minus) / 2
  )
}

analytic_jacobian <- function(x) {
  theta_right <- x[1] * rad_per_deg
  theta_left <- x[2] * rad_per_deg
  numerator <- x[3] - x[4]
  denominator <- sin(theta_right) - sin(theta_left)
  signed <- numerator / denominator
  if (signed == 0) abort_contract("magnitude_not_differentiable_at_zero")
  direction <- if (signed > 0) 1 else -1
  c(
    direction * (-numerator * cos(theta_right) / denominator^2) * rad_per_deg,
    direction * ( numerator * cos(theta_left)  / denominator^2) * rad_per_deg,
    direction / denominator,
    -direction / denominator
  )
}

finite_difference_jacobian <- function(x) {
  steps <- c(1e-5, 1e-5, 1e-6, 1e-6)
  vapply(seq_along(x), function(index) {
    plus <- x
    minus <- x
    plus[index] <- plus[index] + steps[index]
    minus[index] <- minus[index] - steps[index]
    (caster_magnitude(plus) - caster_magnitude(minus)) / (2 * steps[index])
  }, numeric(1))
}

split_effects <- function(text) {
  if (is.na(text) || !nzchar(trimws(text))) return(character())
  trimws(strsplit(text, ";", fixed = TRUE)[[1]])
}

validate_pair <- function(rows) {
  required <- c(
    "observation_id", "endpoint", "generation", "adjustment_state", "side",
    "sweep_id", "approach_direction", "theta_deg", "gamma_deg",
    "theta_source_id", "theta_source_kind"
  )
  if (!identical(names(rows), required)) {
    abort_contract("invalid_observation_header", paste(names(rows), collapse = ","))
  }
  if (nrow(rows) != 2 || !setequal(rows$endpoint, c("right", "left"))) {
    abort_contract("pair_requires_one_right_and_one_left_endpoint")
  }
  if (anyDuplicated(rows$observation_id)) abort_contract("duplicate_observation_id")
  match_fields <- c(
    "generation", "adjustment_state", "side", "sweep_id",
    "approach_direction", "theta_source_id", "theta_source_kind"
  )
  for (field in match_fields) {
    if (any(!nzchar(rows[[field]])) || length(unique(rows[[field]])) != 1) {
      abort_contract("incompatible_observation_provenance", field)
    }
  }
  right <- rows[rows$endpoint == "right", , drop = FALSE]
  left <- rows[rows$endpoint == "left", , drop = FALSE]
  c(
    number(right$theta_deg, "right.theta_deg"),
    number(left$theta_deg, "left.theta_deg"),
    number(right$gamma_deg, "right.gamma_deg"),
    number(left$gamma_deg, "left.gamma_deg")
  )
}

source_covariance <- function(source_id, cells) {
  source_cells <- cells[cells$source_id == source_id, , drop = FALSE]
  expected <- expand.grid(
    row_label = input_labels, column_label = input_labels,
    stringsAsFactors = FALSE
  )
  actual_keys <- paste(source_cells$row_label, source_cells$column_label, sep = "\r")
  expected_keys <- paste(expected$row_label, expected$column_label, sep = "\r")
  if (nrow(source_cells) != 16 || anyDuplicated(actual_keys) ||
      !setequal(actual_keys, expected_keys)) {
    abort_contract("covariance_must_name_all_16_cells_once", source_id)
  }
  matrix_value <- matrix(0, nrow = 4, ncol = 4,
                         dimnames = list(input_labels, input_labels))
  for (index in seq_len(nrow(source_cells))) {
    row <- source_cells[index, ]
    matrix_value[row$row_label, row$column_label] <-
      number(row$value, paste(source_id, row$row_label, row$column_label, sep = "."))
  }
  if (max(abs(matrix_value - t(matrix_value))) > 1e-12) {
    abort_contract("covariance_not_symmetric", source_id)
  }
  eigenvalues <- eigen(matrix_value, symmetric = TRUE, only.values = TRUE)$values
  if (min(eigenvalues) < -1e-10) {
    abort_contract("covariance_not_positive_semidefinite", source_id)
  }
  matrix_value
}

read_covariance_sources <- function(case_dir, policy, jacobian) {
  sources_path <- file.path(case_dir, "sources.tsv")
  covariance_path <- file.path(case_dir, "covariance.tsv")
  if (!file.exists(sources_path) && !file.exists(covariance_path)) return(NULL)
  if (!file.exists(sources_path) || !file.exists(covariance_path)) {
    abort_contract("sources_and_covariance_must_be_supplied_together")
  }

  sources <- read_tsv(sources_path)
  cells <- read_tsv(covariance_path)
  if (!identical(names(sources), c(
    "source_id", "kind", "covered_effects", "provenance", "empirical_status"
  ))) abort_contract("invalid_sources_header")
  if (!identical(names(cells), c(
    "source_id", "row_label", "column_label", "value"
  ))) abort_contract("invalid_covariance_header")
  if (nrow(sources) < 1 || any(!nzchar(sources$source_id)) ||
      anyDuplicated(sources$source_id)) abort_contract("invalid_or_duplicate_source_id")
  allowed_kinds <- c(
    "measurement_repeatability", "instrument_resolution", "steering_angle",
    "calibration_shared", "between_pair", "between_session", "model",
    "joint_covariance", "shared_systematic"
  )
  if (any(!sources$kind %in% allowed_kinds)) {
    abort_contract("unknown_error_source_kind",
                   paste(setdiff(sources$kind, allowed_kinds), collapse = ";"))
  }
  if (!setequal(unique(cells$source_id), sources$source_id)) {
    abort_contract("covariance_source_identity_mismatch")
  }
  if (nrow(sources) > 1 &&
      (is.null(policy[["independence_assertion"]]) ||
       !nzchar(trimws(policy[["independence_assertion"]])))) {
    abort_contract("missing_independence_assertion")
  }

  claimed_effects <- character()
  total <- matrix(0, 4, 4)
  contributions <- numeric()
  for (index in seq_len(nrow(sources))) {
    source <- sources[index, ]
    effects <- split_effects(source$covered_effects)
    overlap <- intersect(claimed_effects, effects)
    if (length(overlap)) {
      abort_contract("double_counted_uncertainty", paste(overlap, collapse = ";"))
    }
    claimed_effects <- c(claimed_effects, effects)
    covariance <- source_covariance(source$source_id, cells)
    contribution <- as.numeric(t(jacobian) %*% covariance %*% jacobian)
    contributions[source$source_id] <- contribution
    total <- total + covariance
  }
  total_variance <- as.numeric(t(jacobian) %*% total %*% jacobian)
  if (total_variance < -1e-10) abort_contract("negative_propagated_variance")
  list(
    sources = sources,
    effects = claimed_effects,
    contributions = contributions,
    variance = max(0, total_variance),
    status = if (all(sources$empirical_status == "empirical"))
      "probabilistic_standard_error" else "illustrative_only_not_error_bar"
  )
}

read_bounds <- function(path, center, jacobian) {
  if (!file.exists(path)) return(NULL)
  rows <- read_tsv(path)
  if (!identical(names(rows), c(
    "input_label", "radius", "source_kind", "provenance"
  ))) abort_contract("invalid_bounds_header")
  if (nrow(rows) != 4 || anyDuplicated(rows$input_label) ||
      !setequal(rows$input_label, input_labels)) {
    abort_contract("bounds_must_name_all_four_inputs_once")
  }
  radii <- setNames(numeric(4), input_labels)
  for (index in seq_len(nrow(rows))) {
    radius <- number(rows$radius[index], paste0("radius.", rows$input_label[index]))
    if (radius < 0) abort_contract("negative_bound_radius", rows$input_label[index])
    radii[rows$input_label[index]] <- radius
  }
  radii <- as.numeric(radii[input_labels])
  linear_radius <- sum(abs(jacobian) * radii)
  center_output <- caster_magnitude(center)

  theta_right_range <- center[1] + c(-radii[1], radii[1])
  theta_left_range <- center[2] + c(-radii[2], radii[2])
  if (min(theta_right_range, theta_left_range) < -90 ||
      max(theta_right_range, theta_left_range) > 90) {
    abort_contract("nonlinear_box_requires_monotone_sine_angle_ranges")
  }
  denominator_range <- c(
    sin(theta_right_range[1] * rad_per_deg) -
      sin(theta_left_range[2] * rad_per_deg),
    sin(theta_right_range[2] * rad_per_deg) -
      sin(theta_left_range[1] * rad_per_deg)
  )
  denominator_range <- sort(denominator_range)
  if (denominator_range[1] <= 0 && denominator_range[2] >= 0) {
    abort_contract("nonlinear_box_contains_steering_singularity")
  }
  numerator_center <- center[3] - center[4]
  numerator_radius <- radii[3] + radii[4]
  numerator_range <- numerator_center + c(-numerator_radius, numerator_radius)
  candidates <- abs(as.vector(outer(
    numerator_range, denominator_range, FUN = "/"
  )))
  nonlinear_lower <- if (numerator_range[1] <= 0 && numerator_range[2] >= 0) {
    0
  } else {
    min(candidates)
  }
  nonlinear_upper <- max(candidates)
  list(
    kind = paste(unique(rows$source_kind), collapse = ";"),
    radii = radii,
    linear_lower = center_output - linear_radius,
    linear_upper = center_output + linear_radius,
    nonlinear_lower = nonlinear_lower,
    nonlinear_upper = nonlinear_upper,
    nonlinear_minus = center_output - nonlinear_lower,
    nonlinear_plus = nonlinear_upper - center_output,
    coverage = "complete_box_interval"
  )
}

audit_resampling <- function(path, covariance_effects) {
  if (is.null(path) || !file.exists(path)) return(NULL)
  rows <- read_tsv(path)
  if (!identical(names(rows), c(
    "sampling_structure", "resampling_unit", "group_id", "pair_id", "pair_role",
    "covered_effects", "provenance"
  ))) abort_contract("invalid_resampling_header")
  if (length(unique(rows$sampling_structure)) != 1 ||
      length(unique(rows$resampling_unit)) != 1) {
    abort_contract("inconsistent_resampling_plan")
  }
  structure <- rows$sampling_structure[1]
  unit <- rows$resampling_unit[1]
  if (structure == "designed" && unit == "steering_position") {
    abort_contract("designed_positions_not_iid")
  }
  effects <- unique(unlist(lapply(rows$covered_effects, split_effects)))
  overlap <- intersect(effects, covariance_effects)
  if (length(overlap)) {
    abort_contract("bootstrap_measurement_error_double_count", paste(overlap, collapse = ";"))
  }
  group_count <- length(unique(rows$group_id))
  if (group_count < 2) abort_contract("fewer_than_two_resampling_groups")

  if (any(!nzchar(rows$pair_id))) abort_contract("missing_odd_even_pair_id")
  if (any(!rows$pair_role %in% c("plus", "minus"))) {
    abort_contract("invalid_odd_even_pair_role")
  }
  groups <- unique(rows$group_id)
  reference_pairs <- NULL
  for (group_id in groups) {
    group_rows <- rows[rows$group_id == group_id, , drop = FALSE]
    pair_ids <- sort(unique(group_rows$pair_id))
    if (is.null(reference_pairs)) {
      reference_pairs <- pair_ids
    } else if (!identical(pair_ids, reference_pairs)) {
      abort_contract("odd_even_pair_set_mismatch_between_resampling_groups")
    }
    for (pair_id in pair_ids) {
      roles <- sort(group_rows$pair_role[group_rows$pair_id == pair_id])
      if (!identical(roles, c("minus", "plus"))) {
        abort_contract(
          "odd_even_pair_incomplete_within_resampling_group",
          paste(group_id, pair_id, sep = ":")
        )
      }
    }
  }
  list(structure = structure, unit = unit, group_count = group_count,
       effects = effects, pair_count = length(reference_pairs))
}

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) < 1) abort_contract("usage", "caster_receipt.R CASE_DIR [--resampling FILE]")
case_dir <- normalizePath(arguments[1], mustWork = TRUE)
resampling_path <- NULL
if (length(arguments) > 1) {
  if (length(arguments) != 3 || arguments[2] != "--resampling") {
    abort_contract("usage", "caster_receipt.R CASE_DIR [--resampling FILE]")
  }
  resampling_path <- arguments[3]
}

policy <- read_policy(file.path(case_dir, "policy.tsv"))
observations <- read_tsv(file.path(case_dir, "observations.tsv"))
inputs <- validate_pair(observations)
jacobian <- analytic_jacobian(inputs)
numeric_jacobian <- finite_difference_jacobian(inputs)
derivative_error <- max(abs(jacobian - numeric_jacobian))
if (derivative_error > 1e-8) abort_contract("finite_difference_jacobian_mismatch")

covariance <- read_covariance_sources(case_dir, policy, jacobian)
bounds <- read_bounds(file.path(case_dir, "bounds.tsv"), inputs, jacobian)
if (is.null(resampling_path)) {
  candidate <- file.path(case_dir, "resampling.tsv")
  if (file.exists(candidate)) resampling_path <- candidate
}
covariance_effects <- if (is.null(covariance)) character() else covariance$effects
resampling <- audit_resampling(resampling_path, covariance_effects)

right <- observations[observations$endpoint == "right", ]
left <- observations[observations$endpoint == "left", ]
odd_even <- odd_even_components(inputs[3], inputs[4])
emit("receipt_version", "caster-uncertainty-v1")
emit("implementation", "R")
emit("calculation_role", "regression_oracle")
emit("numeric_carrier", "binary64_reference")
emit("case_id", policy[["case_id"]])
emit("status", "PASS")
emit("estimate_kind", policy[["estimate_kind"]])
emit("generation", right$generation)
emit("adjustment_state", right$adjustment_state)
emit("side", right$side)
emit("sweep_id", right$sweep_id)
emit("approach_direction", right$approach_direction)
emit("right_observation_id", right$observation_id)
emit("left_observation_id", left$observation_id)
emit("theta_source_id", right$theta_source_id)
emit("theta_source_kind", right$theta_source_kind)
emit("input_order", paste(input_labels, collapse = ","))
emit("input_values", paste(vapply(inputs, format_number, character(1)), collapse = ","))
emit("signed_coefficient_deg", format_number(signed_coefficient(inputs)))
emit("caster_magnitude_deg", format_number(caster_magnitude(inputs)))
emit("odd_camber_component_deg", format_number(odd_even[["odd"]]))
emit("even_camber_component_deg", format_number(odd_even[["even"]]))
emit("jacobian_values", paste(vapply(jacobian, format_number, character(1)), collapse = ","))
emit("jacobian_units", "deg_per_deg,deg_per_deg,deg_per_deg,deg_per_deg")
emit("finite_difference_max_abs_error", format_number(derivative_error))
emit("unresolved_effects", policy[["unresolved_effects"]])

if (is.null(covariance)) {
  emit("covariance_status", "not_supplied")
  emit("error_bar_status", "not_computed")
} else {
  emit("covariance_status", covariance$status)
  emit("covariance_source_ids", paste(covariance$sources$source_id, collapse = ";"))
  emit("propagated_variance_deg2", format_number(covariance$variance))
  emit("propagated_standard_deviation_deg", format_number(sqrt(covariance$variance)))
  for (source_id in names(covariance$contributions)) {
    emit(paste0("variance_contribution.", source_id),
         format_number(covariance$contributions[[source_id]]))
  }
  emit("error_bar_status", covariance$status)
}

if (is.null(bounds)) {
  emit("bounds_status", "not_supplied")
} else {
  emit("bounds_status", bounds$kind)
  emit("bounds_coverage", bounds$coverage)
  emit("linear_interval_deg", paste(
    format_number(bounds$linear_lower), format_number(bounds$linear_upper), sep = ","
  ))
  emit("nonlinear_interval_deg", paste(
    format_number(bounds$nonlinear_lower), format_number(bounds$nonlinear_upper), sep = ","
  ))
  emit("nonlinear_minus_plus_deg", paste(
    format_number(bounds$nonlinear_minus), format_number(bounds$nonlinear_plus), sep = ","
  ))
}

if (is.null(resampling)) {
  emit("resampling_status", "not_requested")
} else {
  emit("resampling_status", "plan_validated_not_executed")
  emit("resampling_unit", resampling$unit)
  emit("independent_group_count", resampling$group_count)
  emit("resampling_pairing", "symmetric_odd_even_pairs_preserved")
  emit("symmetric_pair_count", resampling$pair_count)
}

# Analytically soluble regression: three estimates each have independent
# variance 0.25 and share systematic variance 1.0. Equal GLS weights leave the
# shared component intact instead of dividing it by three.
emit("three_pair_correlated_variance", format_number(1.0 + 0.25 / 3.0))
emit("three_pair_naive_variance", format_number((1.0 + 0.25) / 3.0))
