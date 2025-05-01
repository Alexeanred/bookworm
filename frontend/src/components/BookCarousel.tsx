import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface BookCarouselProps {
  children: React.ReactNode[];
  itemsToShow?: number;
}

const BookCarousel: React.FC<BookCarouselProps> = ({ children, itemsToShow = 4 }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const next = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex + itemsToShow >= children.length ? 0 : prevIndex + 1
    );
  };

  const prev = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? children.length - itemsToShow : prevIndex - 1
    );
  };

  return (
    <div className="relative">
      <div className="overflow-hidden">
        <div 
          className="flex transition-transform duration-300 ease-in-out"
          style={{
            transform: `translateX(-${(currentIndex * (100 / itemsToShow))}%)`,
          }}
        >
          {children.map((child, index) => (
            <div 
              key={index}
              className="flex-none w-full sm:w-1/2 md:w-1/3 lg:w-1/4 px-2"
            >
              {child}
            </div>
          ))}
        </div>
      </div>
      
      <button
        onClick={prev}
        className="absolute left-0 top-1/2 -translate-y-1/2 bg-white/80 p-2 rounded-full shadow-lg hover:bg-white"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>
      
      <button
        onClick={next}
        className="absolute right-0 top-1/2 -translate-y-1/2 bg-white/80 p-2 rounded-full shadow-lg hover:bg-white"
      >
        <ChevronRight className="w-6 h-6" />
      </button>
    </div>
  );
};

export default BookCarousel;