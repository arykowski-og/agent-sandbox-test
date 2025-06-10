import React from 'react';

interface OpenDataIconProps {
  size?: number;
  className?: string;
}

export function OpenDataIcon({ size = 24, className = "" }: OpenDataIconProps) {
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
        <path className="cls-2" d="M10.03,75.95c-3.67-6.14-5.78-13.33-5.78-21,0-22.64,18.36-41,41-41,2.74,0,5.43.27,8.02.78"/>
        <path className="cls-2" d="M86.25,55.08c-.07,22.58-18.4,40.87-41,40.87-7.66,0-14.82-2.1-20.96-5.75"/>
        <path className="cls-2" d="M66.05,49.34c.13,1.83.2,3.71.2,5.61,0,22.64-9.4,41-21,41s-21-18.36-21-41S33.65,13.95,45.25,13.95"/>
        <line className="cls-2" x1="45.25" y1="13.95" x2="45.25" y2="95.95"/>
        <line className="cls-2" x1="4.25" y1="54.95" x2="70.15" y2="54.95"/>
        <line className="cls-2" x1="10.03" y1="33.95" x2="55.18" y2="33.95"/>
        <line className="cls-2" x1="10.03" y1="75.95" x2="80.47" y2="75.95"/>
      </g>
      <g>
        <circle className="cls-2" cx="78.25" cy="21.95" r="9"/>
        <path className="cls-2" d="M62.05,33.69c-2.39-3.3-3.8-7.35-3.8-11.73,0-11.05,8.95-20,20-20s20,8.95,20,20c0,4.38-1.41,8.44-3.8,11.73,0,0-16.2,22.18-16.2,22.18,0,0-16.2-22.18-16.2-22.18Z"/>
      </g>
      <path className="cls-1" d="M23.84,79.76H3.65c-.93,0-1.25,1.22-.45,1.69l9.64,5.56v11.13c0,.93,1.22,1.25,1.69.45l10.09-17.49c.35-.6-.09-1.35-.78-1.35h0Z"/>
    </svg>
  );
} 