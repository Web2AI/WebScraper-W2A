function scraperApp() {
  return {
    primaryUrl: "", // bind primary URL input
    useImageDescriptor: false, // bind image descriptor checkbox
    loading: false, // loading state
    resultMessage: "", // feedback message to user
    resultClass: "", // CSS class for feedback
    depthLimit: 5,

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
          body: JSON.stringify({
            primary_url: this.primaryUrl,
            use_image_descriptor: this.useImageDescriptor,
            depth_limit: this.depthLimit,
          }),
        });

        const data = await response.json();

        console.log(data); // TODO: remove from final

        if (data.results) {
          const websites = data.results.filter((result) => result.json); // TODO: find more robust way for counting scraped websites
          this.resultMessage =
            "Success: " + websites.length + " website(s) scraped";
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
