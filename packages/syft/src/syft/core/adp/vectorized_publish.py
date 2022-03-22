# stdlib
from random import gauss
from typing import Callable
from typing import Tuple

# third party
import numpy as np

# relative
from .data_subject_ledger import DataSubjectLedger
from .entity_list import EntityList


def calculate_bounds_for_mechanism(
    value_array: np.ndarray, min_val_array: np.ndarray, max_val_array: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculates the squared L2 norm values needed to create a Mechanism, and calculate
    privacy budget + spend. If you calculate the privacy budget spend with the worst
    case bound, you can show this number to the DS. If you calculate it with the
    regular value (the value computed below when public_only = False, you cannot show
    the privacy budget to the DS because this violates privacy."""

    # TODO: Double check whether the iDPGaussianMechanism class squares its
    # squared_l2_norm values!!

    # using np.ones_like dtype=value_array.dtype because without it the output was
    # of type "O" python object causing issues when doing operations against JAX
    worst_case_l2_norm = np.sqrt(
        np.sum(np.square(max_val_array - min_val_array))
    ) * np.ones_like(value_array, dtype=value_array.dtype)

    l2_norm = np.sqrt(np.sum(np.square(value_array))) * np.ones_like(
        value_array, dtype=value_array.dtype
    )

    # print(l2_norm.shape, worst_case_l2_norm.shape)
    # print(l2_norm.shape)
    return l2_norm, worst_case_l2_norm


def vectorized_publish(
    min_vals: np.ndarray,
    max_vals: np.ndarray,
    values: np.ndarray,
    data_subjects: EntityList,
    ledger: DataSubjectLedger,
    is_linear: bool = True,
    data_scientist_budget: float = 675,
    sigma: float = 1.5,
    output_func: Callable = np.sum
    # private: bool = False
) -> np.ndarray:
    print("Starting vectorized publish")
    # Get all unique entities
    unique_data_subjects = data_subjects.one_hot_lookup
    # unique_data_subject_indices = np.arange(
    _ = np.arange(
        len(unique_data_subjects)
    )  # because unique_data_subjects returns an array, but we need indices

    print("Obtained data subject indices")

    # Calculate everything needed for RDP
    sigmas = np.reshape(np.ones_like(values) * sigma, -1)
    coeffs = np.ones_like(values).reshape(-1)
    l2_norms, l2_norm_bounds = calculate_bounds_for_mechanism(
        value_array=values, min_val_array=min_vals, max_val_array=max_vals
    )

    if is_linear:
        lipschitz_bounds = np.ones_like(values).reshape(-1)
    else:
        raise Exception("gamma_tensor.lipschitz_bound property would be used here")

    input_entities = data_subjects.entities_indexed[0].reshape(-1)

    print("Obtained all parameters for RDP")

    # if ledger is None:
    #     ledger = DataSubjectLedger()
    print("Initialized ledger!")

    # ledger.reset()
    # Get the Ledger started
    ledger.batch_append(
        sigmas=sigmas,
        l2_norms=l2_norms,
        l2_norm_bounds=l2_norm_bounds,
        Ls=lipschitz_bounds,
        coeffs=coeffs,
        entity_ids=input_entities,
    )

    print("Concluded batch append")

    # Query budget spend of all unique entities
    mask = ledger.get_overbudgeted_entities(
        user_budget=data_scientist_budget, unique_entity_ids_query=input_entities
    )  # unique_data_subject_indices)

    print("Obtained overbudgeted entity mask")

    # TODO: Send this LedgerUpdate to the actual database
    # update = ledger.write_to_db()

    print("Written to DB!")
    ledger.write_to_db()

    # Filter results
    filtered_inputs = values * (
        mask ^ 1
    )  # + gauss(0, sigma)  # Double check that noise has mean of 0
    return output_func(filtered_inputs) + gauss(0, sigma)
