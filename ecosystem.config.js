module.exports = {
  apps: [
    {
      name: "numenex-vali",
      script: "bash",
      args: "cmd /c poetry run python -m src.numenex.validator.numx",
      cwd: "/path/to/your/root/project", // Make sure to set this to your project's root directory
      interpreter: "bash",
      watch: false, // Change to true if you want PM2 to restart on file changes
      vizion: false,
    },
  ],
};
