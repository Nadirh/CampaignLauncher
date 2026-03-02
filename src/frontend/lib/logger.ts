import pino from "pino";

const logger = pino({
  name: "campaign-launcher-frontend",
  level: process.env.LOG_LEVEL || "info",
});

export default logger;
