import React from 'react';

const CoinsCard: React.FC = () => {
  const rewards = [
    {
      networkName: 'PowerShare Platform',
      coins: 120,
      energy: 240,
      txCount: 5,
      rank: 1,
    },
    {
      networkName: 'Green Energy Hub',
      coins: 85,
      energy: 170,
      txCount: 3,
      rank: 2,
    },
    {
      networkName: 'Solar Trade Network',
      coins: 60,
      energy: 120,
      txCount: 2,
      rank: 3,
    },
  ];

  const missions = [
    {
      title: 'Trade 500 kWh in a week',
      reward: '+50 bonus coins',
    },
    {
      title: 'Refer a user who completes 1 trade',
      reward: '+100 coins',
    },
    {
      title: 'Use AI recommendation in a trade',
      reward: '🎖️ Unlock "Smart Trader" Badge',
    },
  ];

  const redeemOptions = [
    'Carbon credits',
    'Discounted energy offers',
    'Premium analytics reports',
    'Wallet top-ups or badges',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-50 px-6 pt-24 space-y-12">
      <h2 className="text-3xl font-bold text-gray-800">⚡ Network Coin Rewards</h2>

      {/* Rewards Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {rewards.map((reward, index) => (
          <div
            key={index}
            className="bg-white border border-gray-200 rounded-xl p-5 shadow hover:shadow-xl transition duration-200"
          >
            <div className="text-xl font-semibold text-blue-600">{reward.networkName}</div>
            <div className="text-gray-500 text-sm mt-1">
              Contributed <strong>{reward.energy} kWh</strong> across <strong>{reward.txCount} txs</strong>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <div className="text-3xl font-bold text-green-500 flex items-center gap-1">
                {reward.coins} <span title="Coin Reward">🪙</span>
              </div>
              <div className="text-sm text-gray-400">Rank #{reward.rank}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Missions Section */}
      <div>
        <h3 className="text-2xl font-semibold text-gray-800 mb-4">🎯 Missions & Achievements</h3>
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {missions.map((mission, i) => (
            <li key={i} className="bg-white rounded-lg shadow p-4 border border-gray-200">
              <div className="font-medium text-gray-700">{mission.title}</div>
              <div className="text-sm text-green-500 mt-1">{mission.reward}</div>
            </li>
          ))}
        </ul>
      </div>

      {/* Redeem Section */}
      <div>
        <h3 className="text-2xl font-semibold text-gray-800 mb-4">🔁 Redeem Coins</h3>
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <p className="text-gray-700 mb-2">Use your coins to unlock:</p>
          <ul className="list-disc pl-5 text-gray-600 space-y-1">
            {redeemOptions.map((option, i) => (
              <li key={i}>{option}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Analytics Placeholder */}
      {/* <div>
        <h3 className="text-2xl font-semibold text-gray-800 mb-4">📈 Coin Earning Analytics</h3>
        <div className="bg-white rounded-xl p-6 border border-gray-200 text-center text-gray-500">
          [Future Feature] Visual dashboards showing your coin trends, earning sources, and AI-predicted growth!
        </div>
      </div> */}
    </div>
  );
};

export default CoinsCard;
