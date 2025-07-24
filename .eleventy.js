module.exports = function(eleventyConfig) {
  // Copy static assets
  eleventyConfig.addPassthroughCopy("src/public");
  eleventyConfig.addPassthroughCopy("src/assets");
  
  // Watch for changes in CSS and JS files
  eleventyConfig.addWatchTarget("src/public/");
  eleventyConfig.addWatchTarget("src/assets/");
  
  // Create collections
  eleventyConfig.addCollection("guides", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/guides/*.md");
  });
  
  eleventyConfig.addCollection("germanGuides", function(collectionApi) {
    return collectionApi.getFilteredByTag("german").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  eleventyConfig.addCollection("europeanGuides", function(collectionApi) {
    return collectionApi.getFilteredByTag("european").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  eleventyConfig.addCollection("automotiveGuides", function(collectionApi) {
    return collectionApi.getFilteredByTag("automotive").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  eleventyConfig.addCollection("themeParks", function(collectionApi) {
    return collectionApi.getFilteredByTag("theme-parks").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  eleventyConfig.addCollection("shopping", function(collectionApi) {
    return collectionApi.getFilteredByTag("shopping").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  eleventyConfig.addCollection("alpine", function(collectionApi) {
    return collectionApi.getFilteredByTag("alpine").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  eleventyConfig.addCollection("coastal", function(collectionApi) {
    return collectionApi.getFilteredByTag("coastal").sort((a, b) => {
      return a.data.title.localeCompare(b.data.title);
    });
  });
  
  // Add filters
  eleventyConfig.addFilter("excerpt", function(content) {
    const excerpt = content.replace(/(<([^>]+)>)/gi, "");
    return excerpt.substr(0, 200) + "...";
  });
  
  eleventyConfig.addFilter("readingTime", function(content) {
    const wordsPerMinute = 200;
    const numberOfWords = content.split(/\s/g).length;
    return Math.ceil(numberOfWords / wordsPerMinute);
  });
  
  // Configuration
  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};