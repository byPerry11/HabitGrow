import { type ReactNode } from 'react'
import clsx from 'clsx'

interface CardProps {
    children: ReactNode
    className?: string
}

export function Card({ children, className }: CardProps) {
    return (
        <div
            className={clsx(
                'bg-white rounded-xl shadow-sm border border-gray-100',
                'transition-all duration-400 ease-smooth',
                'hover:shadow-md',
                className
            )}
        >
            {children}
        </div>
    )
}
