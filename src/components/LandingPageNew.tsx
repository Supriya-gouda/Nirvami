import { motion, useScroll, useTransform } from "motion/react";
import { 
  MessageCircle, 
  Mic, 
  PenLine, 
  Palette, 
  Camera,
  Wind,
  Flame,
  Droplets,
  ArrowRight,
  Heart,
  Brain,
  Leaf,
  Sparkles
} from "lucide-react";
import { Button } from "./ui/button";
import type { User } from "../App";
import logo from "figma:asset/34629939463a62914e4d6cf8617751092b770df0.png";

interface LandingPageProps {
  onGetStarted: () => void;
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header - Exact from Figma */}
      <motion.header 
        className="bg-[rgba(245,230,211,0.95)] shadow-[0px_1px_3px_0px_rgba(0,0,0,0.1),0px_1px_2px_-1px_rgba(0,0,0,0.1)] sticky top-0 z-50 backdrop-blur-sm"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 h-20 flex items-center justify-between">
          {/* Left - Menu & About */}
          <div className="flex items-center gap-6">
            <motion.button 
              className="font-['Arial'] text-[16px] text-[#364153] hover:text-gray-900 transition-colors relative group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Menu
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-emerald-600 group-hover:w-full transition-all duration-300" />
            </motion.button>
            <motion.button 
              onClick={() => scrollToSection('about-section')}
              className="font-['Arial'] text-[16px] text-[#364153] hover:text-gray-900 transition-colors relative group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              About
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-emerald-600 group-hover:w-full transition-all duration-300" />
            </motion.button>
          </div>

          {/* Center - Logo */}
          <motion.div 
            className="absolute left-1/2 -translate-x-1/2 flex flex-col items-center"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.img 
              src={logo} 
              alt="Nirvami Logo" 
              className="w-[72px] h-[72px] mb-[-8px]"
              animate={{ 
                rotate: [0, 5, -5, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            <span className="font-['Arial'] text-[14px] text-[#101828] tracking-[0.7px] uppercase">
              NIRVAMI
            </span>
          </motion.div>

          {/* Right - Get Started */}
          <div className="flex items-center gap-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                onClick={onGetStarted}
                className="bg-[#009966] hover:bg-[#008855] text-white rounded-lg h-8 px-4 text-[14px] shadow-lg hover:shadow-xl transition-all"
              >
                Get Started
              </Button>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <section className="py-20 px-6 bg-gradient-to-b from-[#f5e6d3] to-white relative overflow-hidden">
        {/* Floating background elements */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full bg-emerald-200/20"
              style={{
                width: Math.random() * 200 + 100,
                height: Math.random() * 200 + 100,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, Math.random() * 50 - 25, 0],
                x: [0, Math.random() * 50 - 25, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: Math.random() * 10 + 10,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>

        <div className="max-w-7xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            style={{ opacity, scale }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <h1 className="text-5xl md:text-6xl text-gray-900 mb-6">
                Your Journey to
                <motion.span 
                  className="block mt-2 bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent"
                  animate={{
                    backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
                  }}
                  transition={{
                    duration: 5,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                  style={{
                    backgroundSize: "200% 200%"
                  }}
                >
                  Mental Wellness
                </motion.span>
              </h1>
            </motion.div>
            <motion.p 
              className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              Experience the harmony of ancient Ayurvedic wisdom and modern AI technology. 
              Personalized guidance for your mind, body, and spirit.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  onClick={onGetStarted}
                  size="lg"
                  className="bg-[#009966] hover:bg-[#008855] text-white text-lg px-8 shadow-xl hover:shadow-2xl transition-all group"
                >
                  Begin Your Journey
                  <motion.div
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </motion.div>
                </Button>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <motion.h2 
              className="text-4xl text-gray-900 mb-4"
              animate={{ 
                scale: [1, 1.02, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              Everything You Need for Wellness
            </motion.h2>
            <p className="text-xl text-gray-600">
              Multiple ways to connect, track, and grow
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: MessageCircle,
                title: "Text Chat",
                description: "Talk to your AI companion about your day.",
                color: "emerald",
                bgColor: "bg-emerald-100",
                textColor: "text-emerald-600",
                gradient: "from-emerald-50 to-emerald-100",
              },
              {
                icon: Mic,
                title: "Voice Mode",
                description: "Speak naturally — your voice carries your mood.",
                color: "blue",
                bgColor: "bg-blue-100",
                textColor: "text-blue-600",
                gradient: "from-blue-50 to-blue-100",
              },
              {
                icon: PenLine,
                title: "Manual Log",
                description: "Track meals, sleep, and feelings.",
                color: "purple",
                bgColor: "bg-purple-100",
                textColor: "text-purple-600",
                gradient: "from-purple-50 to-purple-100",
              },
              {
                icon: Palette,
                title: "Mood Board",
                description: "Express yourself visually.",
                color: "pink",
                bgColor: "bg-pink-100",
                textColor: "text-pink-600",
                gradient: "from-pink-50 to-pink-100",
              },
              {
                icon: Camera,
                title: "Camera Mode",
                description: "Let the AI guide your yoga postures.",
                color: "amber",
                bgColor: "bg-amber-100",
                textColor: "text-amber-600",
                gradient: "from-amber-50 to-amber-100",
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ 
                  y: -10,
                  transition: { duration: 0.3 }
                }}
                className={`group cursor-pointer p-6 rounded-3xl bg-gradient-to-br ${feature.gradient} hover:shadow-2xl transition-all duration-300 relative overflow-hidden`}
              >
                {/* Animated background shimmer */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: "100%" }}
                  transition={{ duration: 0.6 }}
                />
                
                <div className="relative z-10">
                  <motion.div 
                    className={`w-16 h-16 rounded-2xl ${feature.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <feature.icon className={`w-8 h-8 ${feature.textColor}`} />
                  </motion.div>
                  <h3 className="text-xl text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Ayurveda & Yoga Section */}
      <section id="about-section" className="py-20 px-6 bg-gradient-to-b from-emerald-50 to-white">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl text-gray-900 mb-6">
              Ancient Wisdom for Modern Wellness
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Ayurveda and Yoga have been practiced for over 5,000 years to promote mental, 
              physical, and spiritual well-being.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.03 }}
              transition={{ duration: 0.3 }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-emerald-400 rounded-3xl blur-xl opacity-0 group-hover:opacity-30 transition-opacity duration-500" />
              <img
                src="https://images.unsplash.com/photo-1667199021925-5778681d0406?w=800&q=80"
                alt="Ayurveda"
                className="rounded-3xl shadow-2xl w-full h-[400px] object-cover relative z-10 transform transition-transform duration-500 group-hover:scale-[1.02]"
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <motion.div 
                className="flex items-center gap-3 mb-6"
                whileHover={{ x: 10 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <motion.div 
                  className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center"
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.6 }}
                >
                  <Leaf className="w-6 h-6 text-emerald-600" />
                </motion.div>
                <h3 className="text-2xl text-gray-900">Ayurveda</h3>
              </motion.div>
              <p className="text-gray-600 leading-relaxed mb-4">
                Ayurveda teaches that mental health is deeply connected to the balance of your 
                doshas (Vata, Pitta, Kapha). By understanding your unique constitution, you can 
                make lifestyle and dietary choices that promote emotional stability and clarity.
              </p>
              <p className="text-gray-600 leading-relaxed">
                Our AI analyzes your responses to provide personalized Ayurvedic recommendations 
                for diet, herbs, routines, and practices that align with your dosha balance.
              </p>
            </motion.div>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="order-2 md:order-1"
            >
              <motion.div 
                className="flex items-center gap-3 mb-6"
                whileHover={{ x: 10 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <motion.div 
                  className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center"
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.6 }}
                >
                  <Heart className="w-6 h-6 text-teal-600" />
                </motion.div>
                <h3 className="text-2xl text-gray-900">Yoga</h3>
              </motion.div>
              <p className="text-gray-600 leading-relaxed mb-4">
                Yoga is a powerful tool for managing stress, anxiety, and depression. Through 
                physical postures (asanas), breathing exercises (pranayama), and meditation, 
                yoga helps calm the nervous system and cultivate inner peace.
              </p>
              <p className="text-gray-600 leading-relaxed">
                Our platform offers AI-guided yoga sessions with real-time posture feedback 
                through camera detection, ensuring you practice safely and effectively.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.03 }}
              transition={{ duration: 0.3 }}
              className="order-1 md:order-2 relative group"
            >
              <div className="absolute inset-0 bg-teal-400 rounded-3xl blur-xl opacity-0 group-hover:opacity-30 transition-opacity duration-500" />
              <img
                src="https://images.unsplash.com/photo-1552206735-e18f41fe76de?w=800&q=80"
                alt="Yoga"
                className="rounded-3xl shadow-2xl w-full h-[400px] object-cover relative z-10 transform transition-transform duration-500 group-hover:scale-[1.02]"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Dosha Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl text-gray-900 mb-6">
              Discover Your Dosha
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              In Ayurveda, the three doshas represent different energies that govern 
              our physical and mental characteristics. Understanding your dominant dosha 
              helps you achieve balance.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Vata */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all cursor-pointer relative overflow-hidden group"
            >
              {/* Animated border glow */}
              <motion.div
                className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{
                  background: "linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent)",
                }}
                animate={{
                  x: ["-100%", "100%"],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />
              
              <motion.div 
                className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-6 mx-auto"
                whileHover={{ rotate: 360, scale: 1.2 }}
                transition={{ duration: 0.6 }}
              >
                <Wind className="w-8 h-8 text-blue-600" />
              </motion.div>
              <h3 className="text-2xl text-gray-900 text-center mb-4">Vata</h3>
              <p className="text-sm text-gray-600 text-center mb-6 italic">
                Air + Space
              </p>
              <motion.img
                src="https://images.unsplash.com/photo-1737568120928-3600286a297d?w=400&q=80"
                alt="Vata"
                className="w-full h-48 object-cover rounded-2xl mb-6"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.3 }}
              />
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Characteristics:</strong> Creative, energetic, quick-thinking, 
                flexible, enthusiastic
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>When Imbalanced:</strong> Anxiety, restlessness, insomnia, 
                digestive issues
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>Balance with:</strong> Warm foods, routine, grounding practices, 
                gentle yoga, meditation
              </p>
            </motion.div>

            {/* Pitta */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.15 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="bg-gradient-to-br from-orange-50 to-red-50 rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all cursor-pointer relative overflow-hidden group"
            >
              {/* Animated border glow */}
              <motion.div
                className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{
                  background: "linear-gradient(90deg, transparent, rgba(249, 115, 22, 0.3), transparent)",
                }}
                animate={{
                  x: ["-100%", "100%"],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />
              
              <motion.div 
                className="w-16 h-16 rounded-full bg-orange-100 flex items-center justify-center mb-6 mx-auto"
                whileHover={{ rotate: 360, scale: 1.2 }}
                transition={{ duration: 0.6 }}
              >
                <Flame className="w-8 h-8 text-orange-600" />
              </motion.div>
              <h3 className="text-2xl text-gray-900 text-center mb-4">Pitta</h3>
              <p className="text-sm text-gray-600 text-center mb-6 italic">
                Fire + Water
              </p>
              <motion.img
                src="https://images.unsplash.com/photo-1760907217151-10ceb4e43242?w=400&q=80"
                alt="Pitta"
                className="w-full h-48 object-cover rounded-2xl mb-6"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.3 }}
              />
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Characteristics:</strong> Intelligent, focused, ambitious, 
                confident, passionate
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>When Imbalanced:</strong> Anger, irritability, inflammation, 
                perfectionism
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>Balance with:</strong> Cooling foods, moderation, calming activities, 
                restorative yoga
              </p>
            </motion.div>

            {/* Kapha */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all cursor-pointer relative overflow-hidden group"
            >
              {/* Animated border glow */}
              <motion.div
                className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{
                  background: "linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.3), transparent)",
                }}
                animate={{
                  x: ["-100%", "100%"],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />
              
              <motion.div 
                className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-6 mx-auto"
                whileHover={{ rotate: 360, scale: 1.2 }}
                transition={{ duration: 0.6 }}
              >
                <Droplets className="w-8 h-8 text-green-600" />
              </motion.div>
              <h3 className="text-2xl text-gray-900 text-center mb-4">Kapha</h3>
              <p className="text-sm text-gray-600 text-center mb-6 italic">
                Earth + Water
              </p>
              <motion.img
                src="https://images.unsplash.com/photo-1658069570842-b05b738a7440?w=400&q=80"
                alt="Kapha"
                className="w-full h-48 object-cover rounded-2xl mb-6"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.3 }}
              />
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Characteristics:</strong> Calm, stable, nurturing, patient, 
                grounded, loyal
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>When Imbalanced:</strong> Lethargy, depression, weight gain, 
                attachment
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>Balance with:</strong> Light foods, stimulation, vigorous exercise, 
                energizing yoga
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Get Started CTA */}
      <section className="py-20 px-6 bg-gradient-to-br from-emerald-600 to-teal-600 relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute inset-0">
          {[...Array(10)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full bg-white/10"
              style={{
                width: Math.random() * 300 + 100,
                height: Math.random() * 300 + 100,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                filter: "blur(40px)",
              }}
              animate={{
                x: [0, Math.random() * 100 - 50],
                y: [0, Math.random() * 100 - 50],
              }}
              transition={{
                duration: Math.random() * 20 + 10,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl text-white mb-6">
              Ready to Begin Your Wellness Journey?
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Join thousands of users who have transformed their lives with personalized 
              Ayurvedic guidance and AI-powered support.
            </p>
            <Button
              onClick={onGetStarted}
              size="lg"
              className="bg-white text-emerald-600 hover:bg-gray-100 text-lg px-10 py-6"
            >
              Get Started Now
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <p className="text-white/80 text-sm mt-6">
              No credit card required • Free 14-day trial • Cancel anytime
            </p>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 bg-[#1a1a1a] text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src={logo} alt="Nirvami" className="w-10 h-10" />
                <span className="text-xl tracking-wider">NIRVAMI</span>
              </div>
              <p className="text-gray-400 leading-relaxed">
                Your AI-powered companion for holistic mental wellness through 
                Ayurvedic wisdom and modern technology.
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-white mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">AI Chat</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Yoga Guide</a></li>
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="text-white mb-4">Resources</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Ayurveda Guide</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Research</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Community</a></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-white mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
            <p>© 2024 Nirvami. All rights reserved.</p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">Instagram</a>
              <a href="#" className="hover:text-white transition-colors">Twitter</a>
              <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}