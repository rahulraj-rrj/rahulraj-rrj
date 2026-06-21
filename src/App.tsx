import DemoOne from "@/components/ui/demo"

function App() {
  return (
    <div className="dark min-h-screen bg-black text-white flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl w-full text-center">
        <h1 className="text-4xl font-extrabold tracking-tight mb-2 text-white">Rotating Dotted Globe</h1>
        <p className="text-neutral-400 mb-6">
          Interactive wireframe globe rendered using D3.js on HTML5 Canvas.
        </p>
        <div className="flex justify-center border border-neutral-800 rounded-3xl p-6 bg-neutral-950/50 backdrop-blur-md">
          <DemoOne />
        </div>
      </div>
    </div>
  )
}

export default App
