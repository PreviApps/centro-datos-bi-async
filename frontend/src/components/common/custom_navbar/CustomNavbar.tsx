import React from "react"

interface CustomNavbarProps{
	title: string;
	children?: React.ReactNode;
}

export default function CustomNavbar({title, children}: CustomNavbarProps){
	return(
		<>
			<div 
				//className="w-full flex flex-col gap-4 p-5 mb-4 bg-transparent border-2 rounded-2xl" style={{backgroundColor: "rgb(4 166 161)"}}
				className="w-[95%] max-w-7xl mx-auto my-4 flex flex-col gap-4 p-5 border-2 rounded-2xl" 
				>
				<h1>{title}</h1>
				{children && (
					<div className="flex items-center gap-2">
          {children}
        </div>
				)}
			</div>
		</>
	)
}