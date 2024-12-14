// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

struct Proof {
    uint256 tokenId;
    uint256 tokenNum;
    bytes32 root;
    bytes32[] peaks;
    bytes32[] merkleProof;
}

contract MmrERC721 is ERC721 {
    address public immutable creator;
    bytes32 internal mmrRoot = 0;
    uint256 internal lastTokenId = 0;
    uint256 internal numTokens = 0;

    constructor(string memory name, string memory symbol) ERC721(name, symbol) {
        creator = msg.sender;
    }

    modifier onlyCreator() {
        require(
            msg.sender == creator,
            "Only the creator can perform this action"
        );
        _;
    }

    function mint(
        address to,
        Proof calldata prevTokenProof,
        Proof calldata newTokenProof
    ) external onlyCreator {
        if (
            !_verifyMint(
                prevTokenProof,
                newTokenProof,
                mmrRoot,
                lastTokenId,
                numTokens
            )
        ) {
            revert();
        }

        mmrRoot = newTokenProof.root;
        lastTokenId = newTokenProof.tokenId;
        numTokens++;

        _safeMint(to, newTokenProof.tokenId);
    }

    function verify(Proof calldata proof) external view returns (bool valid) {
        valid = proof.root == mmrRoot && _verifyProof(proof);
    }

    function _verifyProof(Proof calldata proof)
        internal
        pure
        returns (bool valid)
    {
        valid = proof.root == _bagPeaks(proof.peaks) && _verifyPeak(proof);
    }

    function _verifyPeak(Proof calldata proof)
        internal
        pure
        returns (bool valid)
    {
        bytes32 peak = _getPeak(proof, type(uint256).max);

        valid = false;

        for (uint256 i = 0; i < proof.peaks.length; i++) {
            if (peak == proof.peaks[i]) {
                valid = true;
                break;
            }
        }
    }

    function _getPeak(Proof calldata proof, uint256 limit)
        internal
        pure
        returns (bytes32 peak)
    {
        assert(proof.tokenNum > 0);

        peak = keccak256(abi.encode(proof.tokenId, proof.tokenNum));
        uint256 tokenIndex = proof.tokenNum - 1;

        for (uint256 i = 0; i < proof.merkleProof.length && i < limit; i++) {
            peak = tokenIndex % 2 == 0
                ? keccak256(abi.encode(peak, proof.merkleProof[i]))
                : keccak256(abi.encode(proof.merkleProof[i], peak));

            tokenIndex >>= 1;
        }
    }

    function _verifyMint(
        Proof calldata prevTokenProof,
        Proof calldata newTokenProof,
        bytes32 prevRoot,
        uint256 prevTokenId,
        uint256 prevNumTokens
    ) internal pure returns (bool valid) {
        valid =
            _verifyProof(newTokenProof) &&
            newTokenProof.tokenNum == prevNumTokens + 1;

        if (prevNumTokens == 0) {
            valid =
                valid &&
                newTokenProof.peaks.length == 1 &&
                newTokenProof.merkleProof.length == 0;
        } else {
            valid =
                valid &&
                prevTokenProof.tokenId == prevTokenId &&
                prevTokenProof.tokenNum == prevNumTokens &&
                prevTokenProof.root == newTokenProof.root &&
                _verifyProof(prevTokenProof) &&
                _verifyAncestryProof(prevTokenProof, prevRoot);
        }
    }

    function _verifyAncestryProof(
        Proof calldata ancestryProof,
        bytes32 prevRoot
    ) internal pure returns (bool valid) {
        valid = prevRoot == _prevRoot(ancestryProof);
    }

    function _prevRoot(Proof calldata ancestryProof)
        internal
        pure
        returns (bytes32 prevRoot)
    {
        assert(ancestryProof.tokenNum > 0);

        uint256 tokenNum = ancestryProof.tokenNum;
        uint256 lastPeakHeight = _trailingZeros(tokenNum);
        bytes32 lastPeak = _getPeak(ancestryProof, lastPeakHeight);

        uint256 numPeaks = _countOnes(tokenNum);
        uint256 numMatchingPeaks = _countOnes(tokenNum & (tokenNum + 1));

        if (tokenNum % 2 == 0) {
            if (lastPeak != ancestryProof.peaks[numMatchingPeaks - 1]) {
                prevRoot = 0;
            } else {
                prevRoot = _bagPeaks(ancestryProof.peaks[:numMatchingPeaks]);
            }
        } else {
            uint256 numRemainingPeaks = numPeaks - numMatchingPeaks;
            prevRoot = keccak256(abi.encode(ancestryProof.tokenId, tokenNum));
            prevRoot = _bagPeaksFrom(
                ancestryProof.merkleProof[lastPeakHeight + 1:lastPeakHeight +
                    numRemainingPeaks],
                prevRoot
            );
            prevRoot = _bagPeaksRevFrom(
                ancestryProof.peaks[:numMatchingPeaks],
                prevRoot
            );
        }
    }

    function _checkRoot(Proof calldata proof)
        internal
        pure
        returns (bool valid)
    {
        assert(proof.peaks.length > 0);

        valid = proof.root == _bagPeaks(proof.peaks);
    }

    function _bagPeaks(bytes32[] calldata peaks)
        internal
        pure
        returns (bytes32 root)
    {
        assert(peaks.length > 0);

        root = _bagPeaksRevFrom(
            peaks[:peaks.length - 1],
            peaks[peaks.length - 1]
        );
    }

    function _bagPeaksFrom(bytes32[] calldata peaks, bytes32 start)
        internal
        pure
        returns (bytes32 root)
    {
        root = start;

        for (uint256 i = 0; i < peaks.length; i++) {
            root = keccak256(abi.encode(peaks[i], root));
        }
    }

    function _bagPeaksRevFrom(bytes32[] calldata peaks, bytes32 start)
        internal
        pure
        returns (bytes32 root)
    {
        root = start;

        for (uint256 i = peaks.length; i > 0; i--) {
            root = keccak256(abi.encode(peaks[i - 1], root));
        }
    }

    function _trailingZeros(uint256 number)
        internal
        pure
        returns (uint256 zeros)
    {
        assert(number != 0);

        zeros = 0;

        while (number % 2 == 0) {
            zeros++;
            number >>= 1;
        }
    }

    function _countOnes(uint256 number) internal pure returns (uint256 ones) {
        ones = 0;

        while (number > 0) {
            ones += (number & 1);
            number >>= 1;
        }
    }
}
