use crate::{
    hash::{Hash, Hashable},
    proof::Proof,
    types::U256,
    utils::*,
};

use core::fmt::Debug;

#[derive(Debug)]
pub struct MMR {
    data: Vec<(Hash, Option<U256>)>,
}

impl MMR {
    pub fn new(item: U256) -> Self {
        let mut mmr = MMR { data: Vec::new() };
        mmr.append(item);
        mmr
    }

    pub fn size(&self) -> u64 {
        self.data.len() as u64
    }

    pub fn leaves(&self) -> u64 {
        mmr_size_to_leaf_count(self.data.len() as u64).unwrap()
    }

    pub fn height(&self) -> u64 {
        most_significant_bit(self.leaves())
    }

    pub fn append(&mut self, item: U256) {
        let current_size = self.data.len() as u64;
        let increment = next_increment(current_size).unwrap();

        let mut mmr_index = current_size;
        let leaf_num = mmr_size_to_leaf_count(current_size).unwrap() + 1;
        self.data
            .push((item.hash_with(leaf_num.into()), Some(item)));

        // Calculate increment - 1 parent nodes
        for _ in 0..increment - 1 {
            // Take the next sibling to the left
            let (left_sibling, _) = self.data[left_sibling(mmr_index) as usize];
            let (right_sibling, _) = self.data[mmr_index as usize];

            // Calculate the parent node
            let parent = left_sibling.hash_with(right_sibling);
            self.data.push((parent, None));

            mmr_index += 1;
        }
    }

    pub fn peaks(&self) -> Vec<Hash> {
        let mmr_size = self.data.len() as u64;
        let mut peaks = Vec::new();
        let mut leaf_count = mmr_size_to_leaf_count(mmr_size).unwrap();
        let mut covered = 0;

        while leaf_count != 0 {
            let msb = most_significant_bit(leaf_count);
            let subtree_size = (1 << (msb + 1)) - 1;

            let peak_index = covered + subtree_size - 1;
            let (peak, _) = self.data[peak_index];
            peaks.push(peak);

            covered += subtree_size;
            leaf_count &= !(1 << msb);
        }

        peaks
    }

    pub fn root(&self) -> Hash {
        bag_peaks(&self.peaks())
    }

    pub fn gen_proof(&self, leaf_index: u64) -> Proof {
        assert!(leaf_index < self.leaves());

        let mut mmr_index = leaf_index_to_mmr_index(leaf_index);

        assert!(mmr_index < self.data.len() as u64);
        assert!(height(mmr_index) == 0);

        let mut merkle_proof = Vec::new();
        let mut sibling_index = sibling(mmr_index);
        let (_, Some(item)) = self.data[mmr_index as usize] else {
            panic!("Invalid leaf index")
        };

        while mmr_index < self.data.len() as u64 && sibling_index < self.data.len() as u64 {
            let (next_sibling, _) = self.data[sibling_index as usize];
            merkle_proof.push(next_sibling);

            mmr_index = parent(mmr_index);
            sibling_index = sibling(mmr_index);
        }

        Proof::new(
            item,
            leaf_index + 1,
            merkle_proof,
            self.peaks(),
            self.root(),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn benchmark_mmr() {
        let items = 170_000;
        let now = Instant::now();

        let mut mmr = MMR::new(0.into());
        let mut last_root = mmr.root();

        for i in 1..items {
            mmr.append(0.into());

            if i == items - 2 {
                last_root = mmr.root();
            }
        }

        println!("MMR generation time: {}s", now.elapsed().as_secs());

        let now = Instant::now();
        let last_proof = mmr.gen_proof(items - 2);
        println!("Proof generation time: {}us", now.elapsed().as_micros());

        let new_proof = mmr.gen_proof(items - 1);

        let now = Instant::now();
        for _ in 0..most_significant_bit(items) + 1 {
            assert!(last_proof.verify());
            assert!(new_proof.verify());
            assert!(last_proof.verify_ancestor(last_root));
        }
        println!(
            "Estimated mint data collection time: {}us",
            now.elapsed().as_micros()
        );

        let now = Instant::now();
        for _ in 0..most_significant_bit(items) + 1 {
            assert!(new_proof.verify());
        }
        println!(
            "Estimated verify data collection time: {}us",
            now.elapsed().as_micros()
        );
    }
}
