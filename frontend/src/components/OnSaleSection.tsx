import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useHomeStore } from '../store/homeStore';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import BookCard from './BookCard';

const BOOKS_PER_PAGE = 4;

const OnSaleSection = () => {
  const { onSaleBooks, isLoading, error, fetchOnSaleBooks } = useHomeStore();
  const [startIdx, setStartIdx] = useState(0);

  useEffect(() => {
    fetchOnSaleBooks();
  }, [fetchOnSaleBooks]);

  const maxIdx = Math.max(0, onSaleBooks.length - BOOKS_PER_PAGE);

  const handlePrev = () => setStartIdx(idx => Math.max(0, idx - BOOKS_PER_PAGE));
  const handleNext = () => setStartIdx(idx => Math.min(maxIdx, idx + BOOKS_PER_PAGE));

  const visibleBooks = onSaleBooks.slice(startIdx, startIdx + BOOKS_PER_PAGE);

  if (isLoading) return <div className="py-8">Loading...</div>;
  if (error) return <div className="py-8 text-red-500">{error}</div>;

  return (
    <section className="py-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">On Sale</h2>
        <Link
          to="/shop?sort=discount_desc&size=10"
          className="text-gray-600 hover:text-blue-600"
        >
          View All ›
        </Link>
      </div>
      <div className="relative border rounded-lg p-4 bg-white">
        <button
          className="absolute left-2 top-1/2 -translate-y-1/2 bg-gray-100 p-2 rounded-full shadow hover:bg-gray-200"
          onClick={handlePrev}
          disabled={startIdx === 0}
        >
          <ChevronLeft />
        </button>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {visibleBooks.map(book => (
            <Link
              key={book.id}
              to={`/product/${book.id}`}
              className="flex flex-col h-full overflow-hidden hover:shadow"
            >
              <BookCard
                title={book.title}
                author={book.author_name || book.author}
                image={book.image}
                originalPrice={book.original_price}
                salePrice={book.final_price}
                rating={book.avg_rating}
                reviews={book.reviews_count}
              />
            </Link>
          ))}
        </div>
        <button
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-gray-100 p-2 rounded-full shadow hover:bg-gray-200"
          onClick={handleNext}
          disabled={startIdx >= maxIdx}
        >
          <ChevronRight />
        </button>
      </div>
    </section>
  );
};

export default OnSaleSection;