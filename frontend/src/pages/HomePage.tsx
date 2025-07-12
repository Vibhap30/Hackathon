import React from 'react'
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';



import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  BoltIcon, 
  GlobeAltIcon, 
  ShieldCheckIcon, 
  ChartBarIcon,
  UserGroupIcon,
  CpuChipIcon,
  ArrowRightIcon,
  PlayCircleIcon
} from '@heroicons/react/24/outline'

const HomePage: React.FC = () => {
  const features = [
    {
      icon: BoltIcon,
      title: "Peer-to-Peer Energy Trading",
      description: "Trade energy directly with other users using blockchain technology for secure, transparent transactions.",
      image: "/images/p2p-trading.svg",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: CpuChipIcon,
      title: "AI-Powered Optimization",
      description: "Leverage advanced AI agents to optimize your energy usage, trading strategies, and maximize savings.",
      image: "/images/ai-optimization.svg",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: UserGroupIcon,
      title: "Community Networks",
      description: "Join energy communities to share resources, reduce costs, and build sustainable local energy networks.",
      image: "/images/community-network.svg",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: GlobeAltIcon,
      title: "Beckn Protocol Integration",
      description: "Seamlessly discover and trade energy across different platforms using the open Beckn protocol.",
      image: "/images/beckn-protocol.svg",
      color: "from-orange-500 to-red-500"
    },
    {
      icon: ShieldCheckIcon,
      title: "Blockchain Security",
      description: "All transactions are secured on the blockchain, ensuring transparency and immutable records.",
      image: "/images/blockchain-security.svg",
      color: "from-indigo-500 to-blue-500"
    },
    {
      icon: ChartBarIcon,
      title: "Advanced Analytics",
      description: "Get detailed insights into your energy usage, trading performance, and carbon footprint reduction.",
      image: "/images/analytics.svg",
      color: "from-teal-500 to-green-500"
    }
  ]

  const stats = [
    { label: "Active Users", value: "10,000+", description: "Growing community of energy traders" },
    { label: "Energy Traded", value: "2.5 GWh", description: "Total energy volume traded" },
    { label: "Carbon Saved", value: "1,200 tons", description: "CO₂ emissions prevented" },
    { label: "Communities", value: "150+", description: "Active energy communities" }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
    






<section className="relative">
  <Swiper
    modules={[Navigation, Pagination, Autoplay]}
    navigation
    pagination={{ clickable: true }}
    autoplay={{ delay: 1500 }}
    loop={true}
    className="mySwiper rounded-xl overflow-hidden"
  >
    
 <SwiperSlide>
  <div className="relative h-[500px]">
   
    <img src="image1.jpeg" alt="Slide 1" className="w-full h-full object-cover" />
<div className="absolute inset-0 bg-black/40 flex flex-col justify-center items-start p-[3rem] text-white">

      <div className="grid lg:grid-cols-2 gap-12 items-center w-full">
        {/* Hero Content */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="text-left"
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            The Future of <span>Energy Trading</span>
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-300 leading-relaxed">
            PowerShare enables decentralized, AI-powered peer-to-peer energy trading 
            for a sustainable and efficient energy ecosystem.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/dashboard" className="btn-primary inline-flex items-center justify-center">
              Get Started
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
            <button className="btn-secondary inline-flex items-center justify-center bg-white/10 border-white/30 text-white hover:bg-white/20">
              <PlayCircleIcon className="mr-2 h-5 w-5" />
              Watch Demo
            </button>
          </div>
        </motion.div>

        {/* Animated Energy Blocks */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative"
        >
          <div className="relative bg-gradient-to-br from-white/10 to-white/5 rounded-3xl p-6 sm:p-8 backdrop-blur-sm border border-white/20">
            <div className="grid grid-cols-2 gap-3 sm:gap-4">
              <div className="bg-green-500/20 rounded-2xl p-3 sm:p-4 energy-flow">
                <BoltIcon className="h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10 lg:h-12 lg:w-12 mx-auto animate-pulse-slow text-green-400" />
                <p className="text-center mt-2 font-semibold text-xs sm:text-sm">Solar Energy</p>
              </div>
              <div className="bg-blue-500/20 rounded-2xl p-3 sm:p-4 energy-flow">
                <CpuChipIcon className="h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10 lg:h-12 lg:w-12 mx-auto animate-pulse-slow text-blue-400" />
                <p className="text-center mt-2 font-semibold text-xs sm:text-sm">AI Trading</p>
              </div>
              <div className="bg-purple-500/20 rounded-2xl p-3 sm:p-4 energy-flow">
                <UserGroupIcon className="h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10 lg:h-12 lg:w-12 mx-auto animate-pulse-slow text-purple-400" />
                <p className="text-center mt-2 font-semibold text-xs sm:text-sm">Community</p>
              </div>
              <div className="bg-emerald-500/20 rounded-2xl p-3 sm:p-4 energy-flow">
                <ShieldCheckIcon className="h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10 lg:h-12 lg:w-12 mx-auto animate-pulse-slow text-emerald-400" />
                <p className="text-center mt-2 font-semibold text-xs sm:text-sm">Blockchain</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  </div>
</SwiperSlide>


    
   <SwiperSlide>
  <div className="relative h-[500px]">
    <img src="/image2.jpg" alt="Slide 2" className="w-full h-full object-cover" />
    <div className="absolute inset-0 bg-black/40 flex flex-col justify-center items-start p-[3rem] text-white">
      <h2 className="text-3xl font-bold mb-4">AI Trading Agents</h2>
      <p className="text-lg mb-4">
        Intelligent agents dynamically generate bids and asks using real-time data, forecasts, and historical trends to optimize energy exchange.
      </p>
      <Link to="/ai-assistant">
  <button className="btn-primary">Explore AI Logic</button>
</Link>

    </div>
  </div>
</SwiperSlide>

<SwiperSlide>
  <div className="relative h-[500px]">
    <img src="/image3.jpg" alt="Slide 3" className="w-full h-full object-cover" />
    <div className="absolute inset-0 bg-black/40 flex flex-col justify-center items-start p-[3rem] text-white">
      <h2 className="text-3xl font-bold mb-4">Blockchain Security</h2>
      <p className="text-lg mb-4">
        Every energy transaction is securely recorded on a distributed ledger, ensuring transparency, immutability, and trust across all nodes.
      </p>
      <button className="btn-primary">Discover Blockchain</button>
    </div>
  </div>
</SwiperSlide>

<SwiperSlide>
  <div className="relative h-[500px]">
    <img src="/image4.jpg" alt="Slide 4" className="w-full h-full object-cover" />
    <div className="absolute inset-0 bg-black/40 flex flex-col justify-center items-start p-[3rem] text-white">
      <h2 className="text-3xl font-bold mb-4">Beckn Protocol</h2>
      <p className="text-lg mb-4">
        Beckn enables seamless API communication between buyers, sellers, and DISCOMs, making energy trading interoperable and scalable.
      </p>
      <Link to="/beckn-protocol">
      <button className="btn-primary">Learn About Beckn</button>
      </Link>
    </div>
  </div>
</SwiperSlide>

  </Swiper>
</section>

 <section className="py-16 bg-white relative">
        <div className="container-main">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card-stat group hover:scale-105 transition-transform duration-300"
              >
                <div className="text-3xl md:text-4xl font-bold text-gradient mb-2 group-hover:scale-110 transition-transform duration-300">
                  {stat.value}
                </div>
                <div className="text-lg font-semibold text-gray-900 mb-1">
                  {stat.label}
                </div>
                <div className="text-sm text-gray-600">
                  {stat.description}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section-padding bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="container-main">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for 
              <span className="text-gradient"> Energy Trading</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built with cutting-edge technology to revolutionize how we trade and consume energy
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card-feature group interactive-hover"
              >
                {/* Feature Icon with Gradient Background - Smaller Size */}
                <div className="relative mb-6">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 rounded-2xl bg-gradient-to-br ${feature.color} p-2 sm:p-3 mx-auto group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-full h-full text-white" />
                  </div>
                  <div className="absolute inset-0 w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 rounded-2xl bg-gradient-to-br from-white/20 to-transparent mx-auto"></div>
                </div>

                {/* Feature Content */}
                <div className="text-center">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4 group-hover:text-green-600 transition-colors duration-300">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                {/* Interactive Elements */}
                <div className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="flex justify-center">
                    <button className="btn-ghost text-sm">
                      Learn More →
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How PowerShare Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Simple steps to start trading energy in our decentralized marketplace
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              {
                step: "01",
                title: "Connect Your Devices",
                description: "Link your solar panels, batteries, and smart meters to monitor energy production and consumption in real-time."
              },
              {
                step: "02", 
                title: "Set Your Preferences",
                description: "Configure AI trading agents with your preferences for automatic energy trading and optimization."
              },
              {
                step: "03",
                title: "Start Trading",
                description: "Buy and sell energy with your community or the broader network using secure blockchain transactions."
              }
            ].map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                className="text-center"
              >
                <div className="bg-gradient-to-r from-blue-600 to-green-600 text-white text-2xl font-bold w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                  {step.step}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {step.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-900 to-green-800 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Transform Your Energy Experience?
            </h2>
            <p className="text-xl mb-8 text-gray-300">
              Join thousands of users already trading energy on PowerShare
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="inline-flex items-center px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors duration-200"
              >
                Start Trading Now
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/community"
                className="inline-flex items-center px-8 py-4 bg-transparent border-2 border-white hover:bg-white hover:text-gray-900 text-white font-semibold rounded-lg transition-colors duration-200"
              >
                Explore Communities
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
