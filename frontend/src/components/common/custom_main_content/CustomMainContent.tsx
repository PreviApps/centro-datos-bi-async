import { ReactNode } from "react"

interface MainLayoutProps {
	children: ReactNode
}

const CustomMainContent: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen w-full bg-[#f3f4f6] text-gray-800 font-sans antialiased">
      <main className="container mx-auto px-4 py-6 md:py-4">
        {children}
      </main>
    </div>
  );
};

export default CustomMainContent;