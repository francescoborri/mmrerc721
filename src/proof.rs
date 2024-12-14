use std::fmt::{Display, Formatter, Result};

use crate::{
    hash::{Hash, Hashable},
    types::U256,
    utils::{bag_peaks, bag_peaks_from_iter},
};

#[derive(Debug, Clone)]
pub struct Proof {
    pub token: U256,
    pub token_num: u64,
    pub leaf: Hash,
    pub root: Hash,
    pub peaks: Vec<Hash>,
    pub merkle_proof: Vec<Hash>,
}

impl Proof {
    pub fn new(
        token: U256,
        token_num: u64,
        merkle_proof: Vec<Hash>,
        peaks: Vec<Hash>,
        root: Hash,
    ) -> Self {
        Proof {
            token,
            token_num,
            leaf: token.hash_with(token_num.into()),
            root,
            peaks,
            merkle_proof,
        }
    }

    pub fn verify(&self) -> bool {
        let mut peak = self.leaf;
        let mut index = self.token_num - 1;

        for sibling in &self.merkle_proof {
            peak = if index % 2 == 0 {
                peak.hash_with(*sibling)
            } else {
                (*sibling).hash_with(peak)
            };

            index >>= 1;
        }

        self.peaks.contains(&peak) && bag_peaks(&self.peaks) == self.root
    }

    /// Verifies the ancestry proof given the root of the ancestor MMR.
    /// If the proof is valid, the MMR which has generated this proof
    /// is a valid descendant of the MMR with root `ancestor_root`, and
    /// they differ only by the insertion of the leaf with index `self.token_num`.
    pub fn verify_ancestor(&self, ancestor_root: Hash) -> bool {
        // `self.token_num` is 1-based, we need to subtract 1 to get
        // the 0-based index of the leaf in the MMR.
        let token_index = self.token_num - 1;

        // Height of the last subtree in the ancestor MMR. It indicates the
        // number of nodes to consider in the merkle proof of the ancestry proof:
        // for example, if the height is 0, the leaf was a peak in the
        // ancestor MMR, and the merkle proof must be ignored.
        let last_peak_height = self.token_num.trailing_zeros();

        // Reconstruction of the peak of the last subtree in the ancestor MMR.
        let mut last_peak = self.leaf;
        let mut index = token_index;

        for i in 0..last_peak_height {
            let sibling = &self.merkle_proof[i as usize];

            last_peak = if index % 2 == 0 {
                last_peak.hash_with(*sibling)
            } else {
                (*sibling).hash_with(last_peak)
            };

            index >>= 1;
        }

        // The number of peaks in the previous MMR version of `succ_mmr` is
        // the number of ones in the binary representation of the number of
        // leaves, which is the `leaf_index + 1`.
        let num_peaks = self.token_num.count_ones();

        // This is the number of peaks which are the same in both MMRs.
        let num_matching_peaks = (self.token_num & (self.token_num + 1)).count_ones();

        // Slice of the peaks which have not changed in the descendant MMR, and
        // they are the first `num_matching_peaks` peaks of the descendant MMR.
        let matching_peaks = &self.peaks[0..num_matching_peaks as usize];

        // If the current leaf number is even, then the descendant MMR has just one
        // more peak than the ancestor MMR, hence the number of matching peaks is
        // exactly the number of peaks in the ancestor MMR. Otherwise, the peaks
        // are different and they must be reconstructed from the merkle proof.
        assert_eq!(num_matching_peaks == num_peaks, self.token_num % 2 == 0);

        let rebuilt_root = if self.token_num % 2 == 0 {
            // If the reconstructed `last_peak` is different from the last peak
            // in the ancestor MMR, then the proof is invalid.
            if matching_peaks[matching_peaks.len() - 1] != last_peak {
                return false;
            }

            // Since the `matching_peaks` are exactly the peaks of the
            // ancestor MMR, the root can be directly computed from them.
            bag_peaks(matching_peaks)
        } else {
            let num_remaining_peaks = num_peaks - num_matching_peaks;

            // `start` is `last_peak_height + 1` because the first node in the
            // merkle proof is the sibling of the current leaf, which is the newly
            // inserted leaf in the descendant MMR and must be ignored. It is
            // substituted by the current leaf in the reconstruction.
            let start = last_peak_height + 1;
            let end = last_peak_height + num_remaining_peaks;

            let remaining_peaks = &self.merkle_proof[start as usize..end as usize];

            // The remaining peaks are not reversed as they are already from right to left.
            // The matching peaks are instead reversed because they are from left to right and
            // since the peaks should be bagged from right to left, they must be reversed.
            let root = bag_peaks_from_iter(remaining_peaks.iter(), &self.leaf);
            bag_peaks_from_iter(matching_peaks.iter().rev(), &root)
        };

        ancestor_root == rebuilt_root
    }
}

impl Default for Proof {
    fn default() -> Self {
        Proof {
            token: 0.into(),
            token_num: 0,
            leaf: Hash::default(),
            root: Hash::default(),
            peaks: Vec::new(),
            merkle_proof: Vec::new(),
        }
    }
}

impl Display for Proof {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        write!(
            f,
            "[{},{},\"{}\",[{}],[{}]]",
            self.token,
            self.token_num,
            self.root,
            self.peaks
                .iter()
                .map(|peak| format!("\"{}\"", peak))
                .collect::<Vec<String>>()
                .join(","),
            self.merkle_proof
                .iter()
                .map(|proof| format!("\"{}\"", proof))
                .collect::<Vec<String>>()
                .join(","),
        )
    }
}
