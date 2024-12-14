use crate::hash::{Hash, Hashable};

/// Returns the number of bits in a number, excluding leading zeros.
///
/// # Example
///
/// The number of bits in `5` is `3`, as the binary representation
/// of `5` is `101`.
fn bit_length(num: u64) -> u64 {
    num.to_ne_bytes().len() as u64 * 8 - num.leading_zeros() as u64
}

/// Returns position of the most significant bit in a number.
/// The position is 0-indexed, with the least significant bit
/// being at position 0.
///
/// # Example
///
/// The most significant bit in `5` is `2`, as the binary representation
/// of `5` is `101`, and the leftmost bit is at position `2` counting from
/// right to left and starting from `0`.
pub fn most_significant_bit(num: u64) -> u64 {
    if num == 0 {
        panic!("most_significant_bit called with 0");
    }

    63 - num.leading_zeros() as u64
}

/// Returns position of the least significant bit in a number.
pub fn least_significant_bit(num: u64) -> u64 {
    num.trailing_zeros() as u64
}

/// Returns `true` if all bits in a number, excluding leading zeros,
/// are set to `1`.
fn is_all_ones(num: u64) -> bool {
    let ones = num.count_ones();
    num.leading_zeros() + ones == 64 && ones > 0
}

pub fn jump_left(num: u64) -> u64 {
    num - (1 << most_significant_bit(num)) + 1
}

/// Returns the size of the MMR containing `leaf_index` leaves.
pub fn leaf_count_to_mmr_size(leaf_count: u64) -> u64 {
    2 * leaf_count - leaf_count.count_ones() as u64
}

/// Returns the number of leaves in an MMR of size `mmr_size`.
pub fn mmr_size_to_leaf_count(mut mmr_size: u64) -> Option<u64> {
    let mut leaf_count = 0;

    for height in (0..bit_length(mmr_size)).rev() {
        let tree_leaf_count = 1 << height;
        let tree_size = 2 * tree_leaf_count - 1;

        if tree_size <= mmr_size {
            leaf_count += tree_leaf_count;
            mmr_size -= tree_size;
        }
    }

    if mmr_size == 0 {
        Some(leaf_count)
    } else {
        None
    }
}

// If the node at `mmr_index` is a leaf, returns the position of the leaf.
pub fn mmr_index_to_leaf_index(mmr_index: u64) -> Option<u64> {
    if height(mmr_index) != 0 {
        None
    } else {
        Some(mmr_size_to_leaf_count(mmr_index + next_increment(mmr_index)?)? - 1)
    }
}

// Return the MMR index of the `leaf_index`-th leaf.
pub fn leaf_index_to_mmr_index(leaf_index: u64) -> u64 {
    let leaf_count = leaf_index + 1;
    let mut mmr_index = leaf_count_to_mmr_size(leaf_count) - 1;

    while height(mmr_index) != 0 {
        mmr_index -= 1;
    }

    mmr_index
}

/// Returns the number of newly created nodes when inserting a leaf to a MMR of size `mmr_size`.
pub fn next_increment(mmr_size: u64) -> Option<u64> {
    Some(if mmr_size == 0 {
        1
    } else {
        (mmr_size_to_leaf_count(mmr_size)? + 1).trailing_zeros() as u64 + 1
    })
}

/// Calculate the height of the 0-indexed `mmr_index` node in the MMR.
pub fn height(mmr_index: u64) -> u64 {
    let mut height = mmr_index + 1;

    while !is_all_ones(height) {
        height = jump_left(height);
    }

    most_significant_bit(height)
}

/// Calculate the parent of the `mmr_index` node in the MMR.
pub fn parent(mmr_index: u64) -> u64 {
    if height(mmr_index + 1) > height(mmr_index) {
        // The node at `mmr_index` is a right child, since the height of
        // the next node is greater, which indicates that the next node
        // is his parent.
        mmr_index + 1
    } else {
        // Otherwise the node at `mmr_index` is a left child, and his parent
        // is the successor of his right sibling.
        right_sibling(mmr_index) + 1
    }
}

/// Returns the index of the left sibling of the `mmr_index` node in the MMR.
pub fn left_sibling(mmr_index: u64) -> u64 {
    mmr_index + 1 - (1 << (height(mmr_index) + 1))
}

/// Returns the index of the right sibling of the `mmr_index` node in the MMR.
pub fn right_sibling(mmr_index: u64) -> u64 {
    mmr_index + (1 << (height(mmr_index) + 1)) - 1
}

/// Returns the index of the sibling of the `mmr_index` node in the MMR.
pub fn sibling(mmr_index: u64) -> u64 {
    if height(mmr_index + 1) > height(mmr_index) {
        left_sibling(mmr_index)
    } else {
        right_sibling(mmr_index)
    }
}

/// Bag the peaks from right to left given a list of peaks.
pub fn bag_peaks(peaks: &[Hash]) -> Hash {
    assert!(!peaks.is_empty());

    bag_peaks_from_iter(
        peaks[0..peaks.len() - 1].iter().rev(),
        &peaks[peaks.len() - 1],
    )
}

/// Bag the peaks from left to right with a given start digest.
pub fn bag_peaks_from_iter<'a, I>(peaks: I, start: &Hash) -> Hash
where
    I: Iterator<Item = &'a Hash>,
{
    peaks.fold(*start, |acc, peak| (*peak).hash_with(acc))
}

#[cfg(test)]
pub mod tests {
    use super::*;

    #[test]
    fn test_bit_length() {
        assert_eq!(bit_length(1), 1);
        assert_eq!(bit_length(2), 2);
        assert_eq!(bit_length(5), 3);
        assert_eq!(bit_length(10), 4);
    }

    #[test]
    fn test_most_significant_bit() {
        assert_eq!(most_significant_bit(1), 0);
        assert_eq!(most_significant_bit(2), 1);
        assert_eq!(most_significant_bit(5), 2);
        assert_eq!(most_significant_bit(10), 3);
    }

    #[test]
    fn test_is_all_ones() {
        assert!(is_all_ones(1));
        assert!(!is_all_ones(2));
        assert!(!is_all_ones(5));
        assert!(!is_all_ones(10));
        assert!(is_all_ones(15));
    }

    #[test]
    fn test_size_increment() {
        assert_eq!(next_increment(0), Some(1));
        assert_eq!(next_increment(1), Some(2));
        assert_eq!(next_increment(3), Some(1));
        assert_eq!(next_increment(4), Some(3));
    }

    #[test]
    fn test_mmr_index_to_leaf_index() {
        assert_eq!(mmr_index_to_leaf_index(0), Some(0));
        assert_eq!(mmr_index_to_leaf_index(1), Some(1));
        assert_eq!(mmr_index_to_leaf_index(2), None);
        assert_eq!(mmr_index_to_leaf_index(3), Some(2));
        assert_eq!(mmr_index_to_leaf_index(4), Some(3));
        assert_eq!(mmr_index_to_leaf_index(10), Some(6));
        assert_eq!(mmr_index_to_leaf_index(11), Some(7));
        assert_eq!(mmr_index_to_leaf_index(22), Some(12));
    }

    #[test]
    fn test_height() {
        assert_eq!(height(0), 0);
        assert_eq!(height(1), 0);
        assert_eq!(height(2), 1);
        assert_eq!(height(3), 0);
        assert_eq!(height(4), 0);
        assert_eq!(height(5), 1);
        assert_eq!(height(6), 2);
    }

    #[test]
    fn test_jump_left_right_sibling() {
        assert_eq!(left_sibling(1), 0);
        assert_eq!(right_sibling(0), 1);
        assert_eq!(left_sibling(4), 3);
        assert_eq!(right_sibling(3), 4);
        assert_eq!(left_sibling(5), 2);
        assert_eq!(right_sibling(2), 5);
    }
}
