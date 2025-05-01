import { useState, useEffect } from "react";
import { FaChevronDown, FaChevronUp } from "react-icons/fa";
import { Link, useSearchParams } from "react-router-dom";
import BookCard from '../components/BookCard';
import { booksApi } from '../services/api/books';
import { API_BASE_URL } from '../services/api';

// Define interfaces for our data types
interface Category {
  id: number;
  name: string;
  description?: string;
  book_count: number;
}

interface Author {
  id: number;
  name: string;
  bio?: string;
  book_count: number;
}

interface Book {
  id: number;
  title: string;
  summary?: string;
  original_price: number;
  discount_price?: number;
  final_price: number;
  cover?: string;
  category_id: number;
  category_name?: string;
  author_id: number;
  author_name?: string;
  reviews_count?: number;
  avg_rating?: number;
  // Compatibility with existing code
  book_title?: string;
  book_price?: number;
  book_cover_photo?: string;
  author?: string;
  image?: string;
  rating?: number;
  reviews?: number;
}

const sortOptions = [
  { value: "discount_desc", label: "Sort by on sale" },
  { value: "popularity_desc", label: "Sort by popularity" },
  { value: "price_asc", label: "Sort by price: low to high" },
  { value: "price_desc", label: "Sort by price: high to low" },
];

const ShopPage = () => {
  // Sử dụng useSearchParams để đồng bộ trạng thái với URL
  const [searchParams, setSearchParams] = useSearchParams();

  // Accordion state
  const [open, setOpen] = useState({
    category: true,
    author: true,
    rating: true,
  });

  // Lấy giá trị từ URL hoặc sử dụng giá trị mặc định
  const getInitialCategory = () => {
    const category = searchParams.get('category');
    return category ? parseInt(category, 10) : null;
  };

  const getInitialAuthor = () => {
    const author = searchParams.get('author');
    return author ? parseInt(author, 10) : null;
  };

  const getInitialRating = () => {
    const rating = searchParams.get('rating');
    return rating ? parseInt(rating, 10) : null;
  };

  const getInitialSort = () => {
    return searchParams.get('sort') || sortOptions[0].value;
  };

  const getInitialShowCount = () => {
    const size = searchParams.get('size');
    return size ? parseInt(size, 10) : 10;
  };

  const getInitialPage = () => {
    const pageParam = searchParams.get('page');
    return pageParam ? parseInt(pageParam, 10) : 1;
  };

  // Khởi tạo state từ URL params
  const [selectedCategory, setSelectedCategoryState] = useState<number | null>(getInitialCategory());
  const [selectedAuthor, setSelectedAuthorState] = useState<number | null>(getInitialAuthor());
  const [selectedRating, setSelectedRatingState] = useState<number | null>(getInitialRating());
  const [sort, setSortState] = useState(getInitialSort());
  const [showCount, setShowCountState] = useState(getInitialShowCount());
  const [page, setPageState] = useState(getInitialPage());

  // Hàm cập nhật URL params
  const updateUrlParams = (params: Record<string, string | null>) => {
    const newParams = new URLSearchParams(searchParams);

    // Cập nhật hoặc xóa các params
    Object.entries(params).forEach(([key, value]) => {
      if (value === null) {
        newParams.delete(key);
      } else {
        newParams.set(key, value);
      }
    });

    // Cập nhật URL mà không reload trang
    setSearchParams(newParams);
  };

  // Các hàm setter tùy chỉnh sẽ cập nhật cả state và URL
  const setSelectedCategory = (value: number | null) => {
    setSelectedCategoryState(value);
    setPageState(1); // Reset trang về 1 trực tiếp
    updateUrlParams({ 'category': value?.toString() || null, 'page': '1' });
  };

  const setSelectedAuthor = (value: number | null) => {
    setSelectedAuthorState(value);
    setPageState(1); // Reset trang về 1 trực tiếp
    updateUrlParams({ 'author': value?.toString() || null, 'page': '1' });
  };

  const setSelectedRating = (value: number | null) => {
    setSelectedRatingState(value);
    setPageState(1); // Reset trang về 1 trực tiếp
    updateUrlParams({ 'rating': value?.toString() || null, 'page': '1' });
  };

  const setSort = (value: string) => {
    setSortState(value);
    setPageState(1); // Reset trang về 1 trực tiếp
    updateUrlParams({ 'sort': value, 'page': '1' });
  };

  const setShowCount = (value: number) => {
    setShowCountState(value);
    setPageState(1); // Reset trang về 1 trực tiếp
    updateUrlParams({ 'size': value.toString(), 'page': '1' });
  };

  const setPage = (value: number) => {
    setPageState(value);
    updateUrlParams({ 'page': value.toString() });
  };

  // Data state
  const [categories, setCategories] = useState<Category[]>([]);
  const [authors, setAuthors] = useState<Author[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const ratings = [1, 2, 3, 4, 5];

  // Fetch books, categories and authors from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch categories
        const categoriesResponse = await fetch(`${API_BASE_URL}/categories/`);
        if (!categoriesResponse.ok) throw new Error('Failed to fetch categories');
        const categoriesData = await categoriesResponse.json();
        setCategories(Array.isArray(categoriesData) ? categoriesData : []);

        // Fetch authors
        const authorsResponse = await fetch(`${API_BASE_URL}/authors/`);
        if (!authorsResponse.ok) throw new Error('Failed to fetch authors');
        const authorsData = await authorsResponse.json();
        setAuthors(Array.isArray(authorsData) ? authorsData : []);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Theo dõi thay đổi URL để cập nhật state
  useEffect(() => {
    // Cập nhật state từ URL khi URL thay đổi
    const categoryParam = searchParams.get('category');
    const authorParam = searchParams.get('author');
    const ratingParam = searchParams.get('rating');
    const sortParam = searchParams.get('sort');
    const sizeParam = searchParams.get('size');
    const pageParam = searchParams.get('page');

    // Cập nhật state mà không gọi lại các hàm setter (để tránh vòng lặp vô hạn)
    if (categoryParam !== null) {
      setSelectedCategoryState(parseInt(categoryParam, 10));
    } else if (categoryParam === null && selectedCategory !== null) {
      setSelectedCategoryState(null);
    }

    if (authorParam !== null) {
      setSelectedAuthorState(parseInt(authorParam, 10));
    } else if (authorParam === null && selectedAuthor !== null) {
      setSelectedAuthorState(null);
    }

    if (ratingParam !== null) {
      setSelectedRatingState(parseInt(ratingParam, 10));
    } else if (ratingParam === null && selectedRating !== null) {
      setSelectedRatingState(null);
    }

    if (sortParam !== null && sortParam !== sort) {
      setSortState(sortParam);
    }

    if (sizeParam !== null) {
      const newSize = parseInt(sizeParam, 10);
      if (newSize !== showCount) {
        setShowCountState(newSize);
      }
    }

    if (pageParam !== null) {
      const newPage = parseInt(pageParam, 10);
      if (newPage !== page) {
        setPageState(newPage);
      }
    }
  }, [searchParams]);

  // Fetch books with filters and sorting
  useEffect(() => {
    const fetchBooks = async () => {
      setLoading(true);
      setError(null);

      try {
        // Use the API service to fetch books
        const response = await booksApi.getBooks({
          category_id: selectedCategory || undefined,
          author_id: selectedAuthor || undefined,
          min_rating: selectedRating || undefined,
          sort_by: sort,
          page: page,
          size: showCount
        });

        // Sử dụng dữ liệu trực tiếp từ API
        setBooks(response.items || []);
        setTotalItems(response.total || 0);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, [selectedCategory, selectedAuthor, selectedRating, sort, page, showCount]);

  // Filter labels
  const filterLabels: string[] = [];

  if (selectedCategory) {
    const category = categories.find(c => c.id === selectedCategory);
    if (category) {
      filterLabels.push(category.name);
    }
  }

  if (selectedAuthor) {
    const author = authors.find(a => a.id === selectedAuthor);
    if (author) {
      filterLabels.push(author.name);
    }
  }

  if (selectedRating) {
    filterLabels.push(`${selectedRating} Star`);
  }

  // Combine all filter labels
  const filterLabel = filterLabels.length > 0
    ? `Filtered by ${filterLabels.join(', ')}`
    : "";

  // Accordion toggle
  const toggle = (type: 'category' | 'author' | 'rating') => setOpen(o => ({ ...o, [type]: !o[type] }));

  // Pagination
  const totalPages = Math.ceil(totalItems / showCount);

  // Handle display range (e.g. "Showing 1-12 of 50 books")
  // Đảm bảo trang hiện tại không vượt quá tổng số trang
  const currentPage = Math.min(page, totalPages || 1);
  const startRange = totalItems === 0 ? 0 : (currentPage - 1) * showCount + 1;
  const endRange = Math.min(currentPage * showCount, totalItems);
  const displayRange = `${startRange}–${endRange}`;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <div className="border-b py-4 px-8 flex items-center justify-between">
        <div className="text-2xl font-bold">
          Books {filterLabel && <span className="text-base font-normal ml-2">({filterLabel})</span>}
        </div>
      </div>
      <div className="flex flex-1 px-8 py-6 gap-8">
        {/* Filter Sidebar */}
        <aside className="w-56">
          <div className="mb-6">
            <div className="font-semibold mb-2">Filter By</div>
            {/* Category Accordion */}
            <div className="mb-2 border rounded">
              <button
                className="w-full flex justify-between items-center px-3 py-2"
                onClick={() => toggle("category")}
              >
                Category {open.category ? <FaChevronUp /> : <FaChevronDown />}
              </button>
              {open.category && (
                <div className="px-3 pb-2">
                  {categories.map(category => (
                    <div
                      key={category.id}
                      className={`cursor-pointer hover:underline py-1 ${selectedCategory === category.id ? 'font-semibold' : ''}`}
                      onClick={() => setSelectedCategory(category.id)}
                    >
                      {category.name} ({category.book_count})
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* Author Accordion */}
            <div className="mb-2 border rounded">
              <button
                className="w-full flex justify-between items-center px-3 py-2"
                onClick={() => toggle("author")}
              >
                Author {open.author ? <FaChevronUp /> : <FaChevronDown />}
              </button>
              {open.author && (
                <div className="px-3 pb-2 max-h-60 overflow-auto">
                  {authors.map(author => (
                    <div
                      key={author.id}
                      className={`cursor-pointer hover:underline py-1 ${selectedAuthor === author.id ? 'font-semibold' : ''}`}
                      onClick={() => setSelectedAuthor(author.id)}
                    >
                      {author.name} ({author.book_count})
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* Rating Accordion */}
            <div className="mb-2 border rounded">
              <button
                className="w-full flex justify-between items-center px-3 py-2"
                onClick={() => toggle("rating")}
              >
                Rating Review {open.rating ? <FaChevronUp /> : <FaChevronDown />}
              </button>
              {open.rating && (
                <div className="px-3 pb-2">
                  {ratings.map(r => (
                    <div
                      key={r}
                      className={`cursor-pointer hover:underline py-1 ${selectedRating === r ? 'font-semibold' : ''}`}
                      onClick={() => setSelectedRating(r)}
                    >
                      {r} Star
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* Clear Filters Button */}
            {(selectedCategory || selectedAuthor || selectedRating) && (
              <button
                className="mt-4 w-full px-3 py-2 bg-gray-200 hover:bg-gray-300 rounded text-center"
                onClick={() => {
                  // Xóa tất cả các bộ lọc và cập nhật URL
                  setSelectedCategoryState(null);
                  setSelectedAuthorState(null);
                  setSelectedRatingState(null);
                  setPageState(1); // Reset trang về 1 trực tiếp

                  // Xóa tất cả các tham số bộ lọc khỏi URL
                  updateUrlParams({
                    'category': null,
                    'author': null,
                    'rating': null,
                    'page': '1'
                  });
                }}
              >
                Clear All Filters
              </button>
            )}
          </div>
        </aside>
        {/* Main Content */}
        <main className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <div>Showing {displayRange} of {totalItems} books</div>
            <div className="flex items-center gap-2">
              <select
                className="border rounded px-2 py-1"
                value={sort}
                onChange={e => setSort(e.target.value)}
              >
                {sortOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
              <select
                className="border rounded px-2 py-1"
                value={showCount}
                onChange={e => setShowCount(Number(e.target.value))}
              >
                {[5, 15, 20, 25].map(count => (
                  <option key={count} value={count}>Show {count}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Book Grid */}
          {loading ? (
            <div className="py-8 text-center">Loading...</div>
          ) : error ? (
            <div className="py-8 text-center text-red-500">{error}</div>
          ) : totalItems === 0 ? (
            <div className="py-8 text-center">No books found matching your filters.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {books.map((book) => (
                <div key={book.id} className="h-full">
                  <Link to={`/product/${book.id}`} className="block h-full hover:shadow">
                    <BookCard
                      title={book.title}
                      author={book.author_name || "Unknown Author"}
                      image={book.cover ? `/covers/${book.cover}.jpg` : '/covers/default.png'}
                      originalPrice={book.original_price}
                      salePrice={book.final_price}
                      rating={book.avg_rating}
                      reviews={book.reviews_count}
                    />
                  </Link>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalItems > 0 && (
            <div className="flex justify-center mt-8 gap-2">
              <button
                className="px-3 py-1 border rounded disabled:opacity-50"
                disabled={page === 1}
                onClick={() => setPage(Math.max(1, page - 1))}
              >
                Previous
              </button>

              {totalPages <= 5 ? (
                // Show all pages if 5 or fewer
                Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    className={`px-3 py-1 border rounded ${page === i + 1 ? "bg-gray-200" : ""}`}
                    onClick={() => setPage(i + 1)}
                  >
                    {i + 1}
                  </button>
                ))
              ) : (
                // Show more pages with ellipsis for many pages
                <>
                  {/* First page */}
                  <button
                    className={`px-3 py-1 border rounded ${page === 1 ? "bg-gray-200" : ""}`}
                    onClick={() => setPage(1)}
                  >
                    1
                  </button>

                  {/* Left ellipsis */}
                  {page > 3 && <span className="px-2">...</span>}

                  {/* Pages before current */}
                  {page > 2 && (
                    <button
                      className="px-3 py-1 border rounded"
                      onClick={() => setPage(page - 1)}
                    >
                      {page - 1}
                    </button>
                  )}

                  {/* Current page (when not first) */}
                  {page !== 1 && (
                    <button
                      className="px-3 py-1 border rounded bg-gray-200"
                      onClick={() => setPage(page)}
                    >
                      {page}
                    </button>
                  )}

                  {/* Next 2 pages after current */}
                  {page < totalPages - 1 && (
                    <button
                      className="px-3 py-1 border rounded"
                      onClick={() => setPage(page + 1)}
                    >
                      {page + 1}
                    </button>
                  )}

                  {page < totalPages - 2 && (
                    <button
                      className="px-3 py-1 border rounded"
                      onClick={() => setPage(page + 2)}
                    >
                      {page + 2}
                    </button>
                  )}

                  {/* Right ellipsis */}
                  {page < totalPages - 3 && <span className="px-2">...</span>}

                  {/* Last page */}
                  {totalPages > 1 && page !== totalPages && (
                    <button
                      className={`px-3 py-1 border rounded ${page === totalPages ? "bg-gray-200" : ""}`}
                      onClick={() => setPage(totalPages)}
                    >
                      {totalPages}
                    </button>
                  )}
                </>
              )}

              <button
                className="px-3 py-1 border rounded disabled:opacity-50"
                disabled={page === totalPages || totalItems === 0}
                onClick={() => setPage(Math.min(totalPages, page + 1))}
              >
                Next
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ShopPage;