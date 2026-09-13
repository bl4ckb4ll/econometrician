from dakota_benchmark.epsilon import EpsilonAlgebra, EpsilonExpression


def test_each_epsilon_squares_to_zero_in_both_explicit_modes():
    for mode in ("square_free", "first_order_ideal"):
        alg = EpsilonAlgebra(mode)
        e = EpsilonExpression.epsilon("a", 1.0, alg)
        assert (e * e).terms == {}


def test_mixed_product_is_preserved_only_in_square_free_mode():
    alg = EpsilonAlgebra("square_free")
    a = EpsilonExpression.epsilon("a", 2.0, alg)
    b = EpsilonExpression.epsilon("b", 3.0, alg)
    assert (a * b).terms == {("a", "b"): 6.0}
    alg2 = EpsilonAlgebra("first_order_ideal")
    a2 = EpsilonExpression.epsilon("a", 2.0, alg2)
    b2 = EpsilonExpression.epsilon("b", 3.0, alg2)
    assert (a2 * b2).terms == {}


def test_no_implicit_algebra_choice():
    try:
        EpsilonAlgebra("unspecified")
    except ValueError:
        pass
    else:
        raise AssertionError("mixed-product semantics must be explicit")
