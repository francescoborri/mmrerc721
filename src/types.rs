use std::{
    fmt::{Debug, Display, Formatter, Result},
    ops::Add,
};

use num::{traits::ToBytes, Zero};
use primitive_types::U256 as _U256;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct U256(pub _U256);

impl U256 {
    pub fn new(id: _U256) -> Self {
        U256(id)
    }
}

impl Add for U256 {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        U256(self.0 + other.0)
    }
}

impl Zero for U256 {
    fn zero() -> Self {
        U256(_U256::zero())
    }

    fn is_zero(&self) -> bool {
        self.0.is_zero()
    }
}

impl Display for U256 {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "{}", self.0)
    }
}

impl ToBytes for U256 {
    type Bytes = [u8; 32];

    fn to_be_bytes(&self) -> [u8; 32] {
        self.0.to_big_endian()
    }

    fn to_le_bytes(&self) -> [u8; 32] {
        self.0.to_little_endian()
    }

    fn to_ne_bytes(&self) -> [u8; 32] {
        self.0.to_little_endian()
    }
}

impl<T: Into<_U256>> From<T> for U256 {
    fn from(id: T) -> Self {
        U256(id.into())
    }
}
