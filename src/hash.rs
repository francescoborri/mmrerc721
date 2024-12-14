use num::traits::ToBytes;
use sha3::{Digest, Keccak256};
use std::fmt::{Debug, Display, Formatter, Result};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub struct Hash {
    data: [u8; 32],
}

pub trait Hashable: ToBytes {
    fn hash(&self) -> Hash;
    fn hash_with(&self, other: Self) -> Hash;
}

impl Hash {
    pub fn new(data: [u8; 32]) -> Self {
        Hash { data }
    }
}

impl Display for Hash {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "0x{}", hex::encode(self.data))
    }
}

impl From<&[u8]> for Hash {
    fn from(data: &[u8]) -> Self {
        Hash::new(data.try_into().unwrap())
    }
}

impl ToBytes for Hash {
    type Bytes = [u8; 32];

    fn to_be_bytes(&self) -> Self::Bytes {
        self.data
    }

    fn to_le_bytes(&self) -> Self::Bytes {
        self.data
    }

    fn to_ne_bytes(&self) -> Self::Bytes {
        self.data
    }
}

impl AsRef<[u8]> for Hash {
    fn as_ref(&self) -> &[u8] {
        &self.data
    }
}

impl<T: ToBytes<Bytes = [u8; 32]>> Hashable for T {
    fn hash(&self) -> Hash {
        Hash::from(Keccak256::digest(self.to_be_bytes()).as_slice())
    }

    fn hash_with(&self, other: T) -> Hash {
        Hash::from(Keccak256::digest([self.to_be_bytes(), other.to_be_bytes()].concat()).as_slice())
    }
}
