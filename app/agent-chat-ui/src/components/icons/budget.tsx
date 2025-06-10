import React from 'react';

interface BudgetIconProps {
  size?: number;
  className?: string;
}

export function BudgetIcon({ size = 24, className = "" }: BudgetIconProps) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 101 101" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <style>
          {`
            .cls-1 {
              fill: #f86a0b;
            }
            .cls-2 {
              fill: none;
              stroke: #4b3fff;
              stroke-linecap: round;
              stroke-linejoin: round;
              stroke-width: 2.7px;
            }
          `}
        </style>
      </defs>
      <g>
        <path className="cls-2" d="M70.56,15.5c12.23,6.98,20.47,20.14,20.47,35.23"/>
        <path className="cls-2" d="M30.28,85.88c-12.15-7-20.32-20.12-20.32-35.15"/>
        <polyline className="cls-2" points="62.76 74.62 49.94 96.82 75.58 96.82"/>
        <path className="cls-2" d="M43.35,57.95c0,2.7,2.34,5.18,6.59,5.18,3.99,0,5.65-1.65,5.65-3.77,0-2.7-2.18-3.71-7.17-5.56-5.46-1.91-11.66-4.39-11.66-11.39,0-6.51,5.67-10.36,13.18-10.36s12.37,3.47,13.18,9.41l-7.06,1.88c0-2.75-1.71-5.18-6.12-5.18-3.36,0-5.65,1.75-5.65,4.24,0,2.75,1.97,3.6,7.8,5.67,4.78,1.75,11.97,4.08,11.97,11.28,0,6.46-5.77,10.49-14.02,10.49-7.71,0-12.64-3.55-13.28-9.55l6.59-2.35h0Z"/>
        <line className="cls-2" x1="46.47" y1="31.41" x2="46.47" y2="26.69"/>
        <line className="cls-2" x1="54.53" y1="31.41" x2="54.53" y2="26.69"/>
        <line className="cls-2" x1="46.47" y1="75.38" x2="46.47" y2="70.66"/>
        <line className="cls-2" x1="54.53" y1="75.38" x2="54.53" y2="70.66"/>
        <path className="cls-2" d="M50.5,18.3c17.91,0,32.43,14.52,32.43,32.43,0,12.48-7.05,23.3-17.38,28.73"/>
        <path className="cls-2" d="M50.5,83.17c-17.91,0-32.43-14.52-32.43-32.43,0-11.87,6.38-22.25,15.89-27.91"/>
        <path className="cls-2" d="M27.26,11.09C13.68,19.07,4.56,33.84,4.56,50.74c0,23.05,16.98,42.14,39.11,45.44"/>
        <path className="cls-2" d="M72.31,91.18c14.37-7.77,24.13-22.97,24.13-40.44,0-23.78-18.07-43.34-41.22-45.71"/>
        <path className="cls-2" d="M50.5,96.68h-.48l-.08.14h25.64l-3.26-5.64"/>
        <line className="cls-2" x1="65.56" y1="79.46" x2="62.76" y2="74.62"/>
      </g>
      <path className="cls-1" d="M50.18,4.19h-20c-.91,0-1.24,1.21-.44,1.66l9.55,5.51v11.03c0,.91,1.21,1.24,1.66.44l10-17.31c.34-.59-.09-1.34-.77-1.34"/>
    </svg>
  );
} 