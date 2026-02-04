import { type ReactNode } from 'react'
import clsx from 'clsx'

interface ButtonProps {
    children: ReactNode
    variant?: 'primary' | 'secondary' | 'ghost'
    onClick?: () => void
    disabled?: boolean
    className?: string
}

export function Button({
    children,
    variant = 'primary',
    onClick,
    disabled,
    className
}: ButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={clsx(
                'px-4 py-2 rounded-lg font-medium',
                'transition-all duration-400 ease-smooth',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                variant === 'primary' && 'bg-zen-green text-white hover:bg-green-500 active:scale-95',
                variant === 'secondary' && 'bg-gray-200 text-zen-earth hover:bg-gray-300 active:scale-95',
                variant === 'ghost' && 'text-zen-earth hover:bg-gray-100 active:scale-95',
                className
            )}
        >
            {children}
        </button>
    )
}
