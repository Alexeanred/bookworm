import React from "react";

const AboutPage: React.FC = () => (
  <div className="min-h-screen bg-white flex flex-col">
    <div className="container mx-auto px-6 py-8 flex-1">
      <h2 className="text-xl font-bold mb-4">About Us</h2>
      <hr className="mb-8" />
      <div className="flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-6 text-center">Welcome to Bookworm</h1>
        <p className="text-lg mb-10 text-center max-w-2xl">
          "Bookworm is an independent New York bookstore and language school with locations in Manhattan and Brooklyn. We specialize in travel books and language classes."
        </p>
        <div className="flex flex-col md:flex-row gap-12 w-full justify-center">
          {/* Our Story */}
          <div className="flex-1 max-w-md">
            <h3 className="text-2xl font-bold mb-3">Our Story</h3>
            <p className="mb-3">The name Bookworm was taken from the original name for New York International Airport, which was renamed JFK in December 1963.</p>
            <p className="mb-3">Our Manhattan store has just moved to the West Village. Our new location is 170 7th Avenue South, at the corner of Perry Street.</p>
            <p>From March 2008 through May 2016, the store was located in the Flatiron District.</p>
          </div>
          {/* Our Vision */}
          <div className="flex-1 max-w-md">
            <h3 className="text-2xl font-bold mb-3">Our Vision</h3>
            <p className="mb-3">One of the last travel bookstores in the country, our Manhattan store carries a range of guidebooks (all 10% off) to suit the needs and tastes of every traveller and budget.</p>
            <p>We believe that a novel or travelogue can be just as valuable a key to a place as any guidebook, and our well-read, well-travelled staff is happy to make reading recommendations for any traveller, book lover, or gift giver.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default AboutPage;
