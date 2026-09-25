#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <ick/imprecise.h>

enum { ROWS = 14, COLS = 26, MAX_N = 14 };

typedef enum {
    FORMAT_BINARY32,
    FORMAT_FLOAT16,
    FORMAT_E4M3,
    FORMAT_E5M2,
    FORMAT_E3M2,
    FORMAT_E5M3_SIGNED_MAGNITUDE
} Format;

typedef struct {
    unsigned long count;
    float sum_abs;
    float max_abs;
} ResidualStats;

typedef struct {
    unsigned long unsupported;
    unsigned long nonzero_to_zero;
} QuantizeStats;

static float
absf_local(float value)
{
    return value < 0.0f ? -value : value;
}

static const char *
format_name(Format format)
{
    switch (format) {
    case FORMAT_BINARY32: return "binary32";
    case FORMAT_FLOAT16: return "Float16";
    case FORMAT_E4M3: return "E4M3";
    case FORMAT_E5M2: return "E5M2";
    case FORMAT_E3M2: return "E3M2";
    case FORMAT_E5M3_SIGNED_MAGNITUDE: return "E5M3+sign";
    }
    return "unknown";
}

static void
record_residual(ResidualStats *stats, float reference, float result)
{
    float residual = absf_local(result - reference);
    ++stats->count;
    stats->sum_abs += residual;
    if (residual > stats->max_abs)
        stats->max_abs = residual;
}

static void
record_vector_residual(ResidualStats *stats,
                       const float *reference,
                       const float *result,
                       int length)
{
    int i;
    for (i = 0; i < length; ++i)
        record_residual(stats, reference[i], result[i]);
}

static void
print_residual(const char *stage,
               Format format,
               const char *mode,
               const ResidualStats *stats)
{
    float mean = stats->count ? stats->sum_abs / (float)stats->count : 0.0f;
    printf("summary,%s,%s,%s,count=%lu,mean_abs=%.9g,max_abs=%.9g\n",
           stage, format_name(format), mode,
           stats->count, mean, stats->max_abs);
}

static float
quantize(Format format, float value, QuantizeStats *stats)
{
    float result = value;

    switch (format) {
    case FORMAT_BINARY32:
        result = value;
        break;
    case FORMAT_FLOAT16:
        result = float16_to_float(float16_from_float(value));
        break;
    case FORMAT_E4M3:
        result = e4m3_to_float(e4m3_from_float(value));
        break;
    case FORMAT_E5M2:
        result = e5m2_to_float(e5m2_from_float(value));
        break;
    case FORMAT_E3M2:
        result = e3m2_to_float(e3m2_from_float(value));
        break;
    case FORMAT_E5M3_SIGNED_MAGNITUDE:
        if (value == 0.0f) {
            result = 0.0f;
        } else {
            float magnitude = absf_local(value);
            E5M3 stored;
            if (!e5m3_from_float(magnitude, &stored)) {
                ++stats->unsupported;
                result = 0.0f;
            } else {
                result = e5m3_to_float(stored);
                if (value < 0.0f)
                    result = -result;
            }
        }
        break;
    }

    if (value != 0.0f && result == 0.0f)
        ++stats->nonzero_to_zero;

    return result;
}

static float
narrow_add(Format format, float left, float right)
{
    switch (format) {
    case FORMAT_FLOAT16:
        return float16_to_float(
            float16_add(float16_from_float(left), float16_from_float(right)));
    case FORMAT_E4M3:
        return e4m3_to_float(
            e4m3_add(e4m3_from_float(left), e4m3_from_float(right)));
    case FORMAT_E5M2:
        return e5m2_to_float(
            e5m2_add(e5m2_from_float(left), e5m2_from_float(right)));
    case FORMAT_E3M2:
        return e3m2_to_float(
            e3m2_add(e3m2_from_float(left), e3m2_from_float(right)));
    default:
        return left + right;
    }
}

static float
narrow_multiply(Format format, float left, float right)
{
    switch (format) {
    case FORMAT_FLOAT16:
        return float16_to_float(
            float16_multiply(float16_from_float(left), float16_from_float(right)));
    case FORMAT_E4M3:
        return e4m3_to_float(
            e4m3_multiply(e4m3_from_float(left), e4m3_from_float(right)));
    case FORMAT_E5M2:
        return e5m2_to_float(
            e5m2_multiply(e5m2_from_float(left), e5m2_from_float(right)));
    case FORMAT_E3M2:
        return e3m2_to_float(
            e3m2_multiply(e3m2_from_float(left), e3m2_from_float(right)));
    default:
        return left * right;
    }
}

static int
has_narrow_arithmetic(Format format)
{
    return format == FORMAT_FLOAT16
        || format == FORMAT_E4M3
        || format == FORMAT_E5M2
        || format == FORMAT_E3M2;
}

static int
load_jacobian(const char *path, float matrix[ROWS][COLS])
{
    FILE *file = fopen(path, "r");
    char line[8192];
    int row;

    if (!file) {
        perror(path);
        return 0;
    }
    if (!fgets(line, sizeof line, file)) {
        fclose(file);
        return 0;
    }

    for (row = 0; row < ROWS; ++row) {
        char *cursor;
        int col;

        if (!fgets(line, sizeof line, file)) {
            fclose(file);
            return 0;
        }

        cursor = strchr(line, ',');
        if (!cursor) {
            fclose(file);
            return 0;
        }
        cursor = strchr(cursor + 1, ',');
        if (!cursor) {
            fclose(file);
            return 0;
        }
        ++cursor;

        for (col = 0; col < COLS; ++col) {
            char *end;
            matrix[row][col] = strtof(cursor, &end);
            if (end == cursor) {
                fclose(file);
                return 0;
            }
            cursor = end;
            if (col + 1 < COLS) {
                if (*cursor != ',') {
                    fclose(file);
                    return 0;
                }
                ++cursor;
            }
        }
    }

    fclose(file);
    return 1;
}

static void
quantize_matrix(Format format,
                const float input[ROWS][COLS],
                float output[ROWS][COLS],
                ResidualStats *residuals,
                QuantizeStats *quantization)
{
    int row, col;
    for (row = 0; row < ROWS; ++row) {
        for (col = 0; col < COLS; ++col) {
            output[row][col] = quantize(format, input[row][col], quantization);
            record_residual(residuals, input[row][col], output[row][col]);
        }
    }
}

static void
quantize_vector(Format format,
                const float *input,
                float *output,
                int length,
                QuantizeStats *stats)
{
    int i;
    for (i = 0; i < length; ++i)
        output[i] = quantize(format, input[i], stats);
}

static void
matvec(const float matrix[ROWS][COLS],
       const float vector[COLS],
       float output[ROWS])
{
    int row, col;
    for (row = 0; row < ROWS; ++row) {
        float sum = 0.0f;
        for (col = 0; col < COLS; ++col)
            sum += matrix[row][col] * vector[col];
        output[row] = sum;
    }
}

static void
matvec_narrow(Format format,
              const float matrix[ROWS][COLS],
              const float vector[COLS],
              float output[ROWS])
{
    int row, col;
    for (row = 0; row < ROWS; ++row) {
        float sum = 0.0f;
        for (col = 0; col < COLS; ++col) {
            float term = narrow_multiply(format, matrix[row][col], vector[col]);
            sum = narrow_add(format, sum, term);
        }
        output[row] = sum;
    }
}

static void
transpose_matvec(const float matrix[ROWS][COLS],
                 const float vector[ROWS],
                 float output[COLS])
{
    int row, col;
    for (col = 0; col < COLS; ++col) {
        float sum = 0.0f;
        for (row = 0; row < ROWS; ++row)
            sum += matrix[row][col] * vector[row];
        output[col] = sum;
    }
}

static void
gram_rows(const float matrix[ROWS][COLS], float gram[MAX_N][MAX_N])
{
    int left, right, col;
    for (left = 0; left < ROWS; ++left) {
        for (right = 0; right < ROWS; ++right) {
            float sum = 0.0f;
            for (col = 0; col < COLS; ++col)
                sum += matrix[left][col] * matrix[right][col];
            gram[left][right] = sum;
        }
    }
}

static int
gaussian_solve(int n,
               const float matrix[MAX_N][MAX_N],
               const float rhs[MAX_N],
               float ridge,
               float result[MAX_N])
{
    float augmented[MAX_N][MAX_N + 1];
    int row, col, pivot;

    for (row = 0; row < n; ++row) {
        for (col = 0; col < n; ++col)
            augmented[row][col] = matrix[row][col]
                                + ((row == col) ? ridge : 0.0f);
        augmented[row][n] = rhs[row];
    }

    for (col = 0; col < n; ++col) {
        int best = col;
        float best_abs = absf_local(augmented[col][col]);

        for (row = col + 1; row < n; ++row) {
            float candidate = absf_local(augmented[row][col]);
            if (candidate > best_abs) {
                best_abs = candidate;
                best = row;
            }
        }

        if (best_abs < 1.0e-8f)
            return 0;

        if (best != col) {
            for (pivot = col; pivot <= n; ++pivot) {
                float temporary = augmented[col][pivot];
                augmented[col][pivot] = augmented[best][pivot];
                augmented[best][pivot] = temporary;
            }
        }

        {
            float divisor = augmented[col][col];
            for (pivot = col; pivot <= n; ++pivot)
                augmented[col][pivot] /= divisor;
        }

        for (row = 0; row < n; ++row) {
            float factor;
            if (row == col)
                continue;
            factor = augmented[row][col];
            for (pivot = col; pivot <= n; ++pivot)
                augmented[row][pivot] -= factor * augmented[col][pivot];
        }
    }

    for (row = 0; row < n; ++row)
        result[row] = augmented[row][n];
    return 1;
}

static int
solve_with_ridge(int n,
                 const float matrix[MAX_N][MAX_N],
                 const float rhs[MAX_N],
                 float result[MAX_N],
                 float *ridge_used)
{
    static const float ridges[] = {
        0.0f, 1.0e-7f, 1.0e-5f, 1.0e-3f, 1.0e-1f
    };
    unsigned i;

    for (i = 0; i < sizeof ridges / sizeof ridges[0]; ++i) {
        if (gaussian_solve(n, matrix, rhs, ridges[i], result)) {
            *ridge_used = ridges[i];
            return 1;
        }
    }
    *ridge_used = -1.0f;
    return 0;
}

static int
pseudoinverse_apply(const float matrix[ROWS][COLS],
                    const float observation[ROWS],
                    float state[COLS],
                    float *ridge_used)
{
    float gram[MAX_N][MAX_N] = {{0}};
    float rhs[MAX_N] = {0};
    float weights[MAX_N] = {0};
    int i;

    gram_rows(matrix, gram);
    for (i = 0; i < ROWS; ++i)
        rhs[i] = observation[i];

    if (!solve_with_ridge(ROWS, gram, rhs, weights, ridge_used))
        return 0;

    transpose_matvec(matrix, weights, state);
    return 1;
}

static void
fill_row_seed(int seed, float vector[ROWS])
{
    int i;
    for (i = 0; i < ROWS; ++i)
        vector[i] = 0.0f;

    switch (seed) {
    case 0:
        vector[0] = 1.0f;
        break;
    case 1:
        vector[3] = 1.0f;
        break;
    case 2:
        vector[7] = 1.0f;
        break;
    case 3:
        vector[13] = 1.0f;
        break;
    case 4:
        for (i = 0; i < ROWS; ++i)
            vector[i] = (i & 1) ? -0.5f : 0.5f;
        break;
    case 5:
        for (i = 0; i < ROWS; ++i)
            vector[i] = ((float)i - 6.5f) / 7.0f;
        break;
    case 6:
        for (i = 0; i < ROWS; ++i)
            vector[i] = (float)((i % 3) - 1);
        break;
    default:
        for (i = 0; i < ROWS; ++i) {
            float magnitude = (float)(i + 1) / 14.0f;
            vector[i] = (i & 1) ? -magnitude : magnitude;
        }
        break;
    }
}

static void
run_full_jacobian(const float reference[ROWS][COLS],
                  Format format,
                  const float stored[ROWS][COLS])
{
    ResidualStats forward_widen = {0};
    ResidualStats forward_narrow = {0};
    ResidualStats inverse_state = {0};
    ResidualStats inverse_stored_state = {0};
    ResidualStats inverse_back_reference = {0};
    ResidualStats self_roundtrip = {0};
    QuantizeStats vector_quantization = {0};
    float max_ridge = 0.0f;
    unsigned inverse_failures = 0;
    int seed;

    for (seed = 0; seed < 8; ++seed) {
        float row_seed[ROWS];
        float state_reference[COLS];
        float state_stored[COLS];
        float observation_reference[ROWS];
        float observation_widen[ROWS];
        float observation_narrow[ROWS];
        float observation_stored[ROWS];
        float recovered[COLS];
        float recovered_stored[COLS];
        float back_reference[ROWS];
        float back_stored[ROWS];
        float ridge = 0.0f;

        fill_row_seed(seed, row_seed);
        transpose_matvec(reference, row_seed, state_reference);
        matvec(reference, state_reference, observation_reference);

        quantize_vector(format, state_reference, state_stored,
                        COLS, &vector_quantization);
        matvec(stored, state_stored, observation_widen);
        record_vector_residual(&forward_widen,
                               observation_reference, observation_widen, ROWS);

        if (has_narrow_arithmetic(format)) {
            matvec_narrow(format, stored, state_stored, observation_narrow);
            record_vector_residual(&forward_narrow,
                                   observation_reference, observation_narrow,
                                   ROWS);
        }

        quantize_vector(format, observation_widen, observation_stored,
                        ROWS, &vector_quantization);

        if (!pseudoinverse_apply(stored, observation_stored,
                                 recovered, &ridge)) {
            ++inverse_failures;
            continue;
        }
        if (ridge > max_ridge)
            max_ridge = ridge;

        record_vector_residual(&inverse_state,
                               state_reference, recovered, COLS);

        quantize_vector(format, recovered, recovered_stored,
                        COLS, &vector_quantization);
        record_vector_residual(&inverse_stored_state,
                               state_reference, recovered_stored, COLS);

        matvec(reference, recovered_stored, back_reference);
        record_vector_residual(&inverse_back_reference,
                               observation_reference, back_reference, ROWS);

        matvec(stored, recovered, back_stored);
        record_vector_residual(&self_roundtrip,
                               observation_stored, back_stored, ROWS);
    }

    print_residual("full14x26_forward", format, "store_then_widen_binary32",
                   &forward_widen);
    if (has_narrow_arithmetic(format))
        print_residual("full14x26_forward", format, "requantize_each_term",
                       &forward_narrow);
    print_residual("full14x26_inverse", format, "state_float32",
                   &inverse_state);
    print_residual("full14x26_inverse", format, "state_requantized",
                   &inverse_stored_state);
    print_residual("full14x26_inverse", format, "back_through_reference_J",
                   &inverse_back_reference);
    print_residual("full14x26_inverse", format, "self_observation_roundtrip",
                   &self_roundtrip);

    printf("diagnostic,full14x26,%s,inverse_failures=%u,max_ridge=%.9g,"
           "vector_unsupported=%lu,vector_nonzero_to_zero=%lu\n",
           format_name(format), inverse_failures, max_ridge,
           vector_quantization.unsupported,
           vector_quantization.nonzero_to_zero);
}

static void
coefficient_matvec(const float matrix[ROWS][COLS],
                   const float state[6],
                   float observation[ROWS])
{
    int row, col;
    for (row = 0; row < ROWS; ++row) {
        float sum = 0.0f;
        for (col = 0; col < 6; ++col)
            sum += matrix[row][col] * state[col];
        observation[row] = sum;
    }
}

static void
coefficient_matvec_narrow(Format format,
                          const float matrix[ROWS][COLS],
                          const float state[6],
                          float observation[ROWS])
{
    int row, col;
    for (row = 0; row < ROWS; ++row) {
        float sum = 0.0f;
        for (col = 0; col < 6; ++col) {
            float term = narrow_multiply(format, matrix[row][col], state[col]);
            sum = narrow_add(format, sum, term);
        }
        observation[row] = sum;
    }
}

static int
coefficient_inverse(const float matrix[ROWS][COLS],
                    const float observation[ROWS],
                    float state[6],
                    float *ridge_used)
{
    float normal[MAX_N][MAX_N] = {{0}};
    float rhs[MAX_N] = {0};
    float solution[MAX_N] = {0};
    int left, right, row;

    for (left = 0; left < 6; ++left) {
        for (right = 0; right < 6; ++right) {
            float sum = 0.0f;
            for (row = 0; row < ROWS; ++row)
                sum += matrix[row][left] * matrix[row][right];
            normal[left][right] = sum;
        }
        {
            float sum = 0.0f;
            for (row = 0; row < ROWS; ++row)
                sum += matrix[row][left] * observation[row];
            rhs[left] = sum;
        }
    }

    if (!solve_with_ridge(6, normal, rhs, solution, ridge_used))
        return 0;

    for (left = 0; left < 6; ++left)
        state[left] = solution[left];
    return 1;
}

static void
fill_coefficient_seed(int seed, float state[6])
{
    static const float diagnostic_reference[6] = {
        -2.02989912f, -8.06428242f, 5.87574387f,
         1.33415151f,  5.04709435f, 8.68212891f
    };
    int i;

    for (i = 0; i < 6; ++i)
        state[i] = 0.0f;

    if (seed < 6) {
        state[seed] = 1.0f;
        return;
    }

    if (seed == 6) {
        for (i = 0; i < 6; ++i)
            state[i] = diagnostic_reference[i];
        return;
    }

    for (i = 0; i < 6; ++i)
        state[i] = (i & 1) ? -(float)(i + 1) / 4.0f
                           :  (float)(i + 1) / 4.0f;
}

static void
run_coefficient_block(const float reference[ROWS][COLS],
                      Format format,
                      const float stored[ROWS][COLS])
{
    ResidualStats forward_widen = {0};
    ResidualStats forward_narrow = {0};
    ResidualStats inverse_state = {0};
    ResidualStats inverse_stored_state = {0};
    ResidualStats inverse_back_reference = {0};
    QuantizeStats vector_quantization = {0};
    unsigned inverse_failures = 0;
    float max_ridge = 0.0f;
    int seed;

    for (seed = 0; seed < 8; ++seed) {
        float state_reference[6];
        float state_stored[6];
        float observation_reference[ROWS];
        float observation_widen[ROWS];
        float observation_narrow[ROWS];
        float observation_stored[ROWS];
        float recovered[6];
        float recovered_stored[6];
        float back_reference[ROWS];
        float ridge = 0.0f;

        fill_coefficient_seed(seed, state_reference);
        coefficient_matvec(reference, state_reference, observation_reference);

        quantize_vector(format, state_reference, state_stored,
                        6, &vector_quantization);
        coefficient_matvec(stored, state_stored, observation_widen);
        record_vector_residual(&forward_widen,
                               observation_reference, observation_widen, ROWS);

        if (has_narrow_arithmetic(format)) {
            coefficient_matvec_narrow(format, stored, state_stored,
                                      observation_narrow);
            record_vector_residual(&forward_narrow,
                                   observation_reference, observation_narrow,
                                   ROWS);
        }

        quantize_vector(format, observation_widen, observation_stored,
                        ROWS, &vector_quantization);

        if (!coefficient_inverse(stored, observation_stored,
                                 recovered, &ridge)) {
            ++inverse_failures;
            continue;
        }
        if (ridge > max_ridge)
            max_ridge = ridge;

        record_vector_residual(&inverse_state,
                               state_reference, recovered, 6);

        quantize_vector(format, recovered, recovered_stored,
                        6, &vector_quantization);
        record_vector_residual(&inverse_stored_state,
                               state_reference, recovered_stored, 6);

        coefficient_matvec(reference, recovered_stored, back_reference);
        record_vector_residual(&inverse_back_reference,
                               observation_reference, back_reference, ROWS);
    }

    print_residual("coeff14x6_forward", format, "store_then_widen_binary32",
                   &forward_widen);
    if (has_narrow_arithmetic(format))
        print_residual("coeff14x6_forward", format, "requantize_each_term",
                       &forward_narrow);
    print_residual("coeff14x6_inverse", format, "state_float32",
                   &inverse_state);
    print_residual("coeff14x6_inverse", format, "state_requantized",
                   &inverse_stored_state);
    print_residual("coeff14x6_inverse", format, "back_through_reference_J",
                   &inverse_back_reference);

    printf("diagnostic,coeff14x6,%s,inverse_failures=%u,max_ridge=%.9g,"
           "vector_unsupported=%lu,vector_nonzero_to_zero=%lu\n",
           format_name(format), inverse_failures, max_ridge,
           vector_quantization.unsupported,
           vector_quantization.nonzero_to_zero);
}

int
main(int argc, char **argv)
{
    static const Format formats[] = {
        FORMAT_BINARY32,
        FORMAT_FLOAT16,
        FORMAT_E4M3,
        FORMAT_E5M2,
        FORMAT_E3M2,
        FORMAT_E5M3_SIGNED_MAGNITUDE
    };
    float reference[ROWS][COLS];
    unsigned format_index;

    if (argc != 2) {
        fprintf(stderr, "usage: %s candidate_large_jacobian.csv\n", argv[0]);
        return 2;
    }

    if (!load_jacobian(argv[1], reference)) {
        fprintf(stderr, "could not read the 14x26 candidate Jacobian\n");
        return 3;
    }

    puts("low_precision_jacobian_residuals_v1");
    puts("reference_arithmetic=binary32");
    puts("residual_convention=result-reference");
    puts("residual_magnitude_is_diagnostic_not_pass_fail");
    puts("E5M3_matrix_policy=unsigned_magnitude_plus_external_sign_and_exact_zero");

    for (format_index = 0;
         format_index < sizeof formats / sizeof formats[0];
         ++format_index) {
        Format format = formats[format_index];
        float stored[ROWS][COLS];
        ResidualStats matrix_residual = {0};
        QuantizeStats matrix_quantization = {0};

        quantize_matrix(format, reference, stored,
                        &matrix_residual, &matrix_quantization);

        print_residual("matrix14x26", format, "storage",
                       &matrix_residual);
        printf("diagnostic,matrix14x26,%s,unsupported=%lu,"
               "nonzero_to_zero=%lu\n",
               format_name(format),
               matrix_quantization.unsupported,
               matrix_quantization.nonzero_to_zero);

        run_coefficient_block(reference, format, stored);
        run_full_jacobian(reference, format, stored);
    }

    puts("report_complete");
    return 0;
}
