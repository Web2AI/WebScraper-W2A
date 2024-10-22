function scraperApp() {
  return {
    url: "", // bind URL input
    loading: false, // loading state
    resultMessage: "", // feedback message to user
    resultClass: "", // CSS class for feedback

    async submitForm() {
      this.loading = true;
      this.resultMessage = "";
      this.resultClass = "";

      try {
        const response = await fetch("/scrape", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: this.url }),
        });

        const data = await response.json();

        console.log(data); // TODO: remove from final

        if (data.results) {
          this.resultMessage =
            "Success: " + data.results.length + " website(s) scraped";
          this.resultClass = "text-green-500";
        } else if (data.error) {
          this.resultMessage = "Error: " + data.error;
          this.resultClass = "text-red-500";
        }
      } catch (error) {
        this.resultMessage = "An unexpected error occurred.";
        this.resultClass = "text-red-500";
      } finally {
        this.loading = false;
      }
    },
  };
}
