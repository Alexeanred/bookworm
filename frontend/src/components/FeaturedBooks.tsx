import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useHomeStore } from '../store/homeStore';
import BookCard from './BookCard';

const TABS = {
  RECOMMENDED: 'Recommended',
  POPULAR: 'Popular'
} as const;

type TabType = keyof typeof TABS;

const FeaturedBooks = () => {
  const [activeTab, setActiveTab] = useState<TabType>('RECOMMENDED');
  const { recommendedBooks, popularBooks, isLoading, error, fetchFeaturedBooks } = useHomeStore();

  useEffect(() => {
    fetchFeaturedBooks();
  }, []);

  const books = activeTab === 'RECOMMENDED' ? recommendedBooks : popularBooks;

  if (isLoading) {
    return <div className="py-8">Loading...</div>;
  }

  if (error) {
    return <div className="py-8 text-red-500">{error}</div>;
  }

  return (
    <section className="py-8">
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold mb-2">Featured Books</h2>
        <div className="inline-flex rounded-lg shadow bg-gray-100">
          {Object.entries(TABS).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key as TabType)}
              className={`px-5 py-2 rounded-lg font-medium transition ${
                activeTab === key
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      <div className="border rounded-lg p-4 bg-white">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {books.map((book) => (
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
      </div>
    </section>
  );
};

export default FeaturedBooks;
