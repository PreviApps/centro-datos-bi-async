import { ReactNode } from "react"

interface MainLayoutProps {
	children: ReactNode
}

const CustomMainContent: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col h-screen w-full bg-[#f3f4f6] text-gray-800 font-sans antialiased overflow-hidden">
      <main className="container mx-auto px-4 py-6 md:py-4">
        {children}
      </main>
    </div>
  );
};

export default CustomMainContent;