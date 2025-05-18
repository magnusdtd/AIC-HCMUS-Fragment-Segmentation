import TechStackBar from './ui/tech-stack-bar';
import { AuroraBackground } from './ui/aurora-background';
import { motion } from 'motion/react';
import { TextGenerateEffect } from './ui/text-generate-effect';

export default function Main(props: { skills: { name: string; logo: string }[] }) {
  return (
    <>
      <AuroraBackground>
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.8, ease: 'easeInOut' }}
          className="relative flex flex-col gap-4 items-center justify-center px-4 text-gray-900 dark:text-gray-100"
        >
          <TextGenerateEffect
            words="GDGoC HCMUS AI Challenge"
            className="text-4xl md:text-7xl lg:text-[120px] font-bold"
          />
          <TextGenerateEffect
            words="Rock Fragment Segmentation App"
            className="text-xl md:text-4xl lg:text-[60px] font-sans"
          />
          <div className="flex gap-4 justify-center">
            <a href="/login">
              <button className="p-[3px] relative">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg" />
                <div className="px-8 py-2 bg-black rounded-[6px] relative group transition duration-200 text-white hover:bg-transparent">
                  Login
                </div>
              </button>
            </a>
            <a href="/register">
              <button className="p-[3px] relative">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg" />
                <div className="px-8 py-2 bg-black rounded-[6px] relative group transition duration-200 text-white hover:bg-transparent">
                  Register
                </div>
              </button>
            </a>
            <a href="https://magnusdtd.github.io/AIC-HCMUS-Fragment-Segmentation/" target="_blank" rel="noopener noreferrer">
              <button className="p-[3px] relative">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg" />
                <div className="px-8 py-2 bg-black rounded-[6px] relative group transition duration-200 text-white hover:bg-transparent">
                  Docs
                </div>
              </button>
            </a>
          </div>
        </motion.div>
      </AuroraBackground>

      {/* Bento Grid Section */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.8, ease: 'easeInOut' }}
        className="w-full max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 md:grid-rows-2 gap-6"
      >
        {/* Left Column: About the App (top), Key Features (bottom) */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white/80 dark:bg-zinc-800/80 rounded-xl shadow-lg p-6 flex flex-col md:col-span-1 md:row-span-1 md:row-start-1 md:col-start-1"
        >
          <h3 className="text-xl font-bold mb-3">About the App</h3>
          <p className="text-gray-700 dark:text-gray-200 text-sm leading-relaxed">
            This application is a full-stack solution for fragment segmentation, built for the HCMUS AI Challenge. It includes a <b>React</b> frontend, a <b>FastAPI</b> backend, and supporting services like <b>PostgreSQL</b>, <b>MinIO</b>, and <b>NGINX</b>. The application is containerized using <b>Docker</b> and orchestrated with <b>Kubernetes</b> for deployment. Monitoring and alerting are handled by <b>Prometheus</b> and <b>Grafana</b>.
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white/80 dark:bg-zinc-800/80 rounded-xl shadow-lg p-6 flex flex-col justify-between md:col-span-1 md:row-span-1 md:row-start-2 md:col-start-1"
        >
          <h3 className="text-xl font-bold mb-3">Key Features</h3>
          <ul className="list-disc pl-5 text-gray-700 dark:text-gray-200 text-sm space-y-1">
            <li>Modern <b>React</b> frontend with <b>TypeScript</b> and <b>TailwindCSS</b></li>
            <li>User authentication with JWT</li>
            <li>Image upload, prediction, and overlaid mask visualization</li>
            <li>Particle Size Distribution (PSD) &amp; CDF chart calculation</li>
            <li>Backend powered by <b>FastAPI</b> and <b>YOLOv11m</b> segmentation</li>
            <li>Async background tasks with <b>Celery</b> and <b>Redis</b></li>
            <li>Object storage via <b>MinIO</b></li>
            <li>Cloud-native deployment: <b>Docker</b>, <b>Kubernetes</b>, <b>GKE</b></li>
            <li>Monitoring &amp; alerting with <b>Prometheus</b> and <b>Grafana</b></li>
          </ul>
        </motion.div>

        {/* Right Column: Architecture */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-white/80 dark:bg-zinc-800 rounded-xl shadow-lg p-8 flex flex-col items-center justify-center md:col-span-2 md:row-span-2 md:col-start-2 md:row-start-1 min-h-[36rem] min-w-[32rem]"
        >
          <h2 className="text-xl md:text-5xl font-extrabold mb-6">Architecture</h2>
          <img
            src="app-architecture.jpg"
            alt="App Architecture"
            className="rounded-lg shadow w-full h-[32rem] object-contain bg-white"
          />
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8, ease: 'easeInOut' }}
      >
        <TechStackBar skills={props.skills} />
      </motion.div>

      {/* Guide Video Section */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.8, ease: 'easeInOut' }}
        className="w-full max-w-4xl mx-auto px-4 py-8"
      >
        <h2 className="text-2xl md:text-4xl font-bold mb-4 text-center">Guide Video</h2>
        <div className="aspect-video rounded-lg overflow-hidden shadow-lg bg-black">
          <iframe
            className="w-full h-full"
            src="https://www.youtube-nocookie.com/embed/Ej9QgA6HQYQ?si=tSBggf0-YrWHzKvV"
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
          ></iframe>
        </div>
      </motion.div>

      {/* Development Team Section */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.8, ease: 'easeInOut' }}
        className="w-full max-w-4xl mx-auto px-4 py-8"
      >
        <h2 className="text-2xl md:text-4xl font-bold mb-4 text-center">Noobers Team</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/80 dark:bg-zinc-800/80 rounded-xl shadow-lg p-6 flex flex-col items-center"
          >
            <img src="https://avatars.githubusercontent.com/u/139754211?v=4" alt="Member 1" className="w-24 h-24 rounded-full mb-3 border-4 border-red-500" />
            <h3 className="font-bold text-lg">Đàm Tiến Đạt</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">Team Lead</p>
            <a href="https://github.com/magnusdtd" className="text-blue-500 hover:underline mt-2" target="_blank" rel="noopener noreferrer">GitHub</a>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/80 dark:bg-zinc-800/80 rounded-xl shadow-lg p-6 flex flex-col items-center"
          >
            <img src="https://avatars.githubusercontent.com/u/151555532?v=4" alt="Member 2" className="w-24 h-24 rounded-full mb-3 border-4 border-pink-400" />
            <h3 className="font-bold text-lg">Nguyễn Gia Bảo</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">AI Engineer</p>
            <a href="https://github.com/NGBao1608" className="text-blue-500 hover:underline mt-2" target="_blank" rel="noopener noreferrer">GitHub</a>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/80 dark:bg-zinc-800/80 rounded-xl shadow-lg p-6 flex flex-col items-center"
          >
            <img src="https://avatars.githubusercontent.com/u/192578309?v=4" alt="Member 3" className="w-24 h-24 rounded-full mb-3 border-4 border-green-400" />
            <h3 className="font-bold text-lg">Huỳnh Cung</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">Frontend Engineer</p>
            <a href="https://github.com/cungh28" className="text-blue-500 hover:underline mt-2" target="_blank" rel="noopener noreferrer">GitHub</a>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/80 dark:bg-zinc-800/80 rounded-xl shadow-lg p-6 flex flex-col items-center"
          >
            <img src="https://avatars.githubusercontent.com/u/149289949?v=4" alt="Member 4" className="w-24 h-24 rounded-full mb-3 border-4 border-blue-400" />
            <h3 className="font-bold text-lg">Đỗ Tiến Đạt</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">Backend Engineer</p>
            <a href="https://github.com/tadtd" className="text-blue-500 hover:underline mt-2" target="_blank" rel="noopener noreferrer">GitHub</a>
          </motion.div>
        </div>
      </motion.div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8, ease: 'easeInOut' }}
        className="w-full bg-zinc-900 text-gray-200 py-6 mt-8"
      >
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between">
          <span className="text-sm">&copy; {new Date().getFullYear()} GDGoC HCMUS AI Challenge - Rock Fragment Segmentation App</span>
          <span className="text-xs mt-2 md:mt-0">Made with <span className="text-red-500">&#10084;</span> by the Noobers Team</span>
        </div>
      </motion.footer>
    </>
  );
}
