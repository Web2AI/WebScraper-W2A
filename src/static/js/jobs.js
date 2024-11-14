function schedulerApp() {
  return {
    jobs: [], // array of jobs
    loading: false, // loading state

    async fetchJobs() {
      this.loading = true;
      try {
        const response = await fetch("/scheduler/jobs", { method: "GET" });
        if (response.ok) {
          const data = await response.json();
          this.jobs = data || [];
        } else {
          console.error("Failed to retrieve jobs");
        }
      } catch (error) {
        console.error("An unexpected error occurred.", error);
      } finally {
        this.loading = false;
      }
    },

    // Method to format date as YYYY-mm-dd HH:MM:ss
    formatDate(dateString) {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = ("0" + (date.getMonth() + 1)).slice(-2);
      const day = ("0" + date.getDate()).slice(-2);
      const hours = ("0" + date.getHours()).slice(-2);
      const minutes = ("0" + date.getMinutes()).slice(-2);
      const seconds = ("0" + date.getSeconds()).slice(-2);
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },

    // Initialization function to fetch jobs on load
    async init() {
      await this.fetchJobs();
    },
  };
}
