// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title PowerShareEnergyTrading
 * @dev Smart contract for peer-to-peer energy trading on PowerShare platform
 * @author PowerShare Team
 */
contract PowerShareEnergyTrading is ReentrancyGuard, Ownable, Pausable {
    using Counters for Counters.Counter;
    
    // State variables
    Counters.Counter private _transactionIds;
    Counters.Counter private _offerIds;
    
    uint256 public constant PLATFORM_FEE_BASIS_POINTS = 200; // 2%
    uint256 public constant BASIS_POINTS_DIVISOR = 10000;
    
    // Enums
    enum EnergyType { SOLAR, WIND, HYDRO, MIXED, GRID }
    enum TransactionStatus { PENDING, MATCHED, IN_PROGRESS, COMPLETED, CANCELLED, DISPUTED }
    enum OfferStatus { ACTIVE, MATCHED, EXPIRED, CANCELLED }
    
    // Structs
    struct EnergyOffer {
        uint256 offerId;
        address seller;
        uint256 energyAmount; // in kWh (scaled by 1e18)
        uint256 pricePerKwh; // in wei per kWh
        EnergyType energyType;
        uint256 availableFrom;
        uint256 availableUntil;
        uint256 maxDistanceKm;
        bool autoAccept;
        OfferStatus status;
        string metadataURI; // IPFS hash for additional data
    }
    
    struct EnergyTransaction {
        uint256 transactionId;
        uint256 offerId;
        address seller;
        address buyer;
        uint256 energyAmount; // in kWh (scaled by 1e18)
        uint256 pricePerKwh; // in wei per kWh
        uint256 totalAmount; // total cost in wei
        uint256 platformFee; // platform fee in wei
        EnergyType energyType;
        TransactionStatus status;
        uint256 createdAt;
        uint256 scheduledDeliveryTime;
        uint256 actualDeliveryTime;
        uint256 settlementTime;
        string deliveryProof; // IPFS hash for delivery proof
    }
    
    struct UserProfile {
        bool isRegistered;
        bool isVerified;
        uint256 totalEnergyTraded;
        uint256 totalTransactions;
        uint256 reputationScore; // 0-1000
        string profileMetadataURI; // IPFS hash
    }
    
    struct CommunityStats {
        uint256 totalEnergyTraded;
        uint256 totalTransactions;
        uint256 carbonOffsetKg;
        uint256 totalSavings;
        uint256 activeMembers;
    }
    
    // Mappings
    mapping(uint256 => EnergyOffer) public energyOffers;
    mapping(uint256 => EnergyTransaction) public energyTransactions;
    mapping(address => UserProfile) public userProfiles;
    mapping(address => uint256[]) public userOffers;
    mapping(address => uint256[]) public userTransactions;
    mapping(bytes32 => CommunityStats) public communityStats;
    mapping(address => bytes32) public userCommunity;
    
    // Events
    event OfferCreated(
        uint256 indexed offerId,
        address indexed seller,
        uint256 energyAmount,
        uint256 pricePerKwh,
        EnergyType energyType
    );
    
    event OfferMatched(
        uint256 indexed offerId,
        uint256 indexed transactionId,
        address indexed buyer,
        uint256 energyAmount
    );
    
    event TransactionCreated(
        uint256 indexed transactionId,
        address indexed seller,
        address indexed buyer,
        uint256 energyAmount,
        uint256 totalAmount
    );
    
    event TransactionStatusUpdated(
        uint256 indexed transactionId,
        TransactionStatus status,
        uint256 timestamp
    );
    
    event EnergyDelivered(
        uint256 indexed transactionId,
        uint256 deliveryTime,
        string deliveryProof
    );
    
    event TransactionSettled(
        uint256 indexed transactionId,
        uint256 settlementTime,
        uint256 sellerAmount,
        uint256 platformFee
    );
    
    event UserRegistered(address indexed user, string profileMetadataURI);
    event UserVerified(address indexed user);
    event CommunityJoined(address indexed user, bytes32 indexed communityId);
    
    // Modifiers
    modifier onlyRegistered() {
        require(userProfiles[msg.sender].isRegistered, "User not registered");
        _;
    }
    
    modifier onlyVerified() {
        require(userProfiles[msg.sender].isVerified, "User not verified");
        _;
    }
    
    modifier validOffer(uint256 offerId) {
        require(offerId <= _offerIds.current(), "Invalid offer ID");
        require(energyOffers[offerId].status == OfferStatus.ACTIVE, "Offer not active");
        _;
    }
    
    modifier validTransaction(uint256 transactionId) {
        require(transactionId <= _transactionIds.current(), "Invalid transaction ID");
        _;
    }
    
    // Constructor
    constructor() {
        _transferOwnership(msg.sender);
    }
    
    /**
     * @dev Register a new user on the platform
     * @param profileMetadataURI IPFS hash containing user profile data
     */
    function registerUser(string memory profileMetadataURI) external {
        require(!userProfiles[msg.sender].isRegistered, "User already registered");
        
        userProfiles[msg.sender] = UserProfile({
            isRegistered: true,
            isVerified: false,
            totalEnergyTraded: 0,
            totalTransactions: 0,
            reputationScore: 500, // Start with neutral reputation
            profileMetadataURI: profileMetadataURI
        });
        
        emit UserRegistered(msg.sender, profileMetadataURI);
    }
    
    /**
     * @dev Verify a user (only owner can verify)
     * @param user Address of the user to verify
     */
    function verifyUser(address user) external onlyOwner {
        require(userProfiles[user].isRegistered, "User not registered");
        userProfiles[user].isVerified = true;
        emit UserVerified(user);
    }
    
    /**
     * @dev Join a community
     * @param communityId Community identifier
     */
    function joinCommunity(bytes32 communityId) external onlyRegistered {
        userCommunity[msg.sender] = communityId;
        communityStats[communityId].activeMembers++;
        emit CommunityJoined(msg.sender, communityId);
    }
    
    /**
     * @dev Create a new energy offer
     * @param energyAmount Amount of energy in kWh (scaled by 1e18)
     * @param pricePerKwh Price per kWh in wei
     * @param energyType Type of energy being offered
     * @param availableFrom Timestamp when energy becomes available
     * @param availableUntil Timestamp until when energy is available
     * @param maxDistanceKm Maximum distance for trading in kilometers
     * @param autoAccept Whether to automatically accept matching requests
     * @param metadataURI IPFS hash for additional offer metadata
     */
    function createEnergyOffer(
        uint256 energyAmount,
        uint256 pricePerKwh,
        EnergyType energyType,
        uint256 availableFrom,
        uint256 availableUntil,
        uint256 maxDistanceKm,
        bool autoAccept,
        string memory metadataURI
    ) external onlyRegistered onlyVerified whenNotPaused nonReentrant {
        require(energyAmount > 0, "Energy amount must be positive");
        require(pricePerKwh > 0, "Price must be positive");
        require(availableFrom < availableUntil, "Invalid availability period");
        require(availableFrom >= block.timestamp, "Availability must be in future");
        
        _offerIds.increment();
        uint256 newOfferId = _offerIds.current();
        
        energyOffers[newOfferId] = EnergyOffer({
            offerId: newOfferId,
            seller: msg.sender,
            energyAmount: energyAmount,
            pricePerKwh: pricePerKwh,
            energyType: energyType,
            availableFrom: availableFrom,
            availableUntil: availableUntil,
            maxDistanceKm: maxDistanceKm,
            autoAccept: autoAccept,
            status: OfferStatus.ACTIVE,
            metadataURI: metadataURI
        });
        
        userOffers[msg.sender].push(newOfferId);
        
        emit OfferCreated(newOfferId, msg.sender, energyAmount, pricePerKwh, energyType);
    }
    
    /**
     * @dev Purchase energy from an offer
     * @param offerId ID of the energy offer
     * @param energyAmount Amount of energy to purchase (scaled by 1e18)
     */
    function purchaseEnergy(
        uint256 offerId,
        uint256 energyAmount
    ) external payable onlyRegistered onlyVerified whenNotPaused nonReentrant validOffer(offerId) {
        EnergyOffer storage offer = energyOffers[offerId];
        
        require(msg.sender != offer.seller, "Cannot buy your own energy");
        require(energyAmount <= offer.energyAmount, "Insufficient energy available");
        require(block.timestamp >= offer.availableFrom, "Energy not yet available");
        require(block.timestamp <= offer.availableUntil, "Energy offer expired");
        
        uint256 totalCost = (energyAmount * offer.pricePerKwh) / 1e18;
        uint256 platformFee = (totalCost * PLATFORM_FEE_BASIS_POINTS) / BASIS_POINTS_DIVISOR;
        uint256 sellerAmount = totalCost - platformFee;
        
        require(msg.value >= totalCost, "Insufficient payment");
        
        // Create transaction
        _transactionIds.increment();
        uint256 newTransactionId = _transactionIds.current();
        
        energyTransactions[newTransactionId] = EnergyTransaction({
            transactionId: newTransactionId,
            offerId: offerId,
            seller: offer.seller,
            buyer: msg.sender,
            energyAmount: energyAmount,
            pricePerKwh: offer.pricePerKwh,
            totalAmount: totalCost,
            platformFee: platformFee,
            energyType: offer.energyType,
            status: TransactionStatus.MATCHED,
            createdAt: block.timestamp,
            scheduledDeliveryTime: 0,
            actualDeliveryTime: 0,
            settlementTime: 0,
            deliveryProof: ""
        });
        
        // Update offer
        offer.energyAmount -= energyAmount;
        if (offer.energyAmount == 0) {
            offer.status = OfferStatus.MATCHED;
        }
        
        // Update user records
        userTransactions[msg.sender].push(newTransactionId);
        userTransactions[offer.seller].push(newTransactionId);
        
        // Update user profiles
        userProfiles[msg.sender].totalTransactions++;
        userProfiles[offer.seller].totalTransactions++;
        userProfiles[offer.seller].totalEnergyTraded += energyAmount;
        
        // Update community stats
        bytes32 buyerCommunity = userCommunity[msg.sender];
        bytes32 sellerCommunity = userCommunity[offer.seller];
        
        if (buyerCommunity != bytes32(0)) {
            communityStats[buyerCommunity].totalTransactions++;
            communityStats[buyerCommunity].totalEnergyTraded += energyAmount;
        }
        
        if (sellerCommunity != bytes32(0) && sellerCommunity != buyerCommunity) {
            communityStats[sellerCommunity].totalTransactions++;
            communityStats[sellerCommunity].totalEnergyTraded += energyAmount;
        }
        
        // Refund excess payment
        if (msg.value > totalCost) {
            payable(msg.sender).transfer(msg.value - totalCost);
        }
        
        emit OfferMatched(offerId, newTransactionId, msg.sender, energyAmount);
        emit TransactionCreated(newTransactionId, offer.seller, msg.sender, energyAmount, totalCost);
    }
    
    /**
     * @dev Confirm energy delivery (called by seller)
     * @param transactionId ID of the transaction
     * @param deliveryProof IPFS hash of delivery proof
     */
    function confirmDelivery(
        uint256 transactionId,
        string memory deliveryProof
    ) external validTransaction(transactionId) {
        EnergyTransaction storage transaction = energyTransactions[transactionId];
        
        require(msg.sender == transaction.seller, "Only seller can confirm delivery");
        require(transaction.status == TransactionStatus.MATCHED || transaction.status == TransactionStatus.IN_PROGRESS, "Invalid transaction status");
        
        transaction.status = TransactionStatus.COMPLETED;
        transaction.actualDeliveryTime = block.timestamp;
        transaction.deliveryProof = deliveryProof;
        
        emit EnergyDelivered(transactionId, block.timestamp, deliveryProof);
        emit TransactionStatusUpdated(transactionId, TransactionStatus.COMPLETED, block.timestamp);
    }
    
    /**
     * @dev Settle a completed transaction (release funds)
     * @param transactionId ID of the transaction
     */
    function settleTransaction(uint256 transactionId) external validTransaction(transactionId) {
        EnergyTransaction storage transaction = energyTransactions[transactionId];
        
        require(transaction.status == TransactionStatus.COMPLETED, "Transaction not completed");
        require(transaction.settlementTime == 0, "Transaction already settled");
        
        // For auto-settlement, allow either party to trigger
        // For disputed transactions, only owner can settle
        require(
            msg.sender == transaction.seller || 
            msg.sender == transaction.buyer || 
            msg.sender == owner(),
            "Unauthorized to settle"
        );
        
        transaction.status = TransactionStatus.COMPLETED;
        transaction.settlementTime = block.timestamp;
        
        uint256 sellerAmount = transaction.totalAmount - transaction.platformFee;
        
        // Transfer funds
        payable(transaction.seller).transfer(sellerAmount);
        payable(owner()).transfer(transaction.platformFee);
        
        // Update reputation scores
        _updateReputationScores(transaction.seller, transaction.buyer, true);
        
        // Calculate carbon offset (simplified)
        uint256 carbonOffset = (transaction.energyAmount * 45) / 100; // 0.45 kg CO2 per kWh
        
        // Update community stats
        bytes32 buyerCommunity = userCommunity[transaction.buyer];
        if (buyerCommunity != bytes32(0)) {
            communityStats[buyerCommunity].carbonOffsetKg += carbonOffset;
            communityStats[buyerCommunity].totalSavings += transaction.totalAmount / 10; // Estimate 10% savings
        }
        
        emit TransactionSettled(transactionId, block.timestamp, sellerAmount, transaction.platformFee);
    }
    
    /**
     * @dev Cancel an energy offer (only seller)
     * @param offerId ID of the offer to cancel
     */
    function cancelOffer(uint256 offerId) external validOffer(offerId) {
        EnergyOffer storage offer = energyOffers[offerId];
        require(msg.sender == offer.seller, "Only seller can cancel offer");
        
        offer.status = OfferStatus.CANCELLED;
    }
    
    /**
     * @dev Cancel a transaction (before completion)
     * @param transactionId ID of the transaction
     */
    function cancelTransaction(uint256 transactionId) external validTransaction(transactionId) {
        EnergyTransaction storage transaction = energyTransactions[transactionId];
        
        require(
            msg.sender == transaction.seller || 
            msg.sender == transaction.buyer,
            "Unauthorized to cancel"
        );
        require(
            transaction.status == TransactionStatus.PENDING || 
            transaction.status == TransactionStatus.MATCHED,
            "Cannot cancel transaction in current status"
        );
        
        transaction.status = TransactionStatus.CANCELLED;
        
        // Refund buyer
        payable(transaction.buyer).transfer(transaction.totalAmount);
        
        // Update offer (restore energy amount)
        EnergyOffer storage offer = energyOffers[transaction.offerId];
        offer.energyAmount += transaction.energyAmount;
        if (offer.status == OfferStatus.MATCHED) {
            offer.status = OfferStatus.ACTIVE;
        }
        
        emit TransactionStatusUpdated(transactionId, TransactionStatus.CANCELLED, block.timestamp);
    }
    
    /**
     * @dev Update reputation scores after transaction completion
     */
    function _updateReputationScores(address seller, address buyer, bool successful) private {
        if (successful) {
            // Increase reputation for both parties
            if (userProfiles[seller].reputationScore < 1000) {
                userProfiles[seller].reputationScore += 5;
            }
            if (userProfiles[buyer].reputationScore < 1000) {
                userProfiles[buyer].reputationScore += 2;
            }
        } else {
            // Decrease reputation for both parties
            if (userProfiles[seller].reputationScore > 5) {
                userProfiles[seller].reputationScore -= 5;
            }
            if (userProfiles[buyer].reputationScore > 2) {
                userProfiles[buyer].reputationScore -= 2;
            }
        }
    }
    
    // View functions
    
    /**
     * @dev Get active offers with pagination
     */
    function getActiveOffers(uint256 start, uint256 limit) external view returns (EnergyOffer[] memory) {
        uint256 totalOffers = _offerIds.current();
        uint256 count = 0;
        
        // Count active offers
        for (uint256 i = 1; i <= totalOffers; i++) {
            if (energyOffers[i].status == OfferStatus.ACTIVE) {
                count++;
            }
        }
        
        uint256 resultSize = limit;
        if (start + limit > count) {
            resultSize = count > start ? count - start : 0;
        }
        
        EnergyOffer[] memory activeOffers = new EnergyOffer[](resultSize);
        uint256 resultIndex = 0;
        uint256 activeIndex = 0;
        
        for (uint256 i = 1; i <= totalOffers && resultIndex < resultSize; i++) {
            if (energyOffers[i].status == OfferStatus.ACTIVE) {
                if (activeIndex >= start) {
                    activeOffers[resultIndex] = energyOffers[i];
                    resultIndex++;
                }
                activeIndex++;
            }
        }
        
        return activeOffers;
    }
    
    /**
     * @dev Get user's transactions
     */
    function getUserTransactions(address user) external view returns (uint256[] memory) {
        return userTransactions[user];
    }
    
    /**
     * @dev Get user's offers
     */
    function getUserOffers(address user) external view returns (uint256[] memory) {
        return userOffers[user];
    }
    
    /**
     * @dev Get community statistics
     */
    function getCommunityStats(bytes32 communityId) external view returns (CommunityStats memory) {
        return communityStats[communityId];
    }
    
    /**
     * @dev Emergency pause (only owner)
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause (only owner)
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Withdraw platform fees (only owner)
     */
    function withdrawFees() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No fees to withdraw");
        payable(owner()).transfer(balance);
    }
}
