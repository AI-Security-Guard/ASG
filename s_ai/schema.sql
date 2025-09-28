PRAGMA foreign_keys=ON;

DROP TABLE IF EXISTS clips;
DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs(
  job_id     TEXT PRIMARY KEY,
  video_path TEXT NOT NULL,
  status     TEXT NOT NULL,
  progress   REAL NOT NULL,
  message    TEXT,
  created_at DATETIME NOT NULL DEFAULT (datetime('now')),
  updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER trg_jobs_updated_at
AFTER UPDATE ON jobs
FOR EACH ROW
BEGIN
  UPDATE jobs SET updated_at = datetime('now') WHERE job_id = OLD.job_id;
END;

CREATE TABLE clips(
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id     TEXT NOT NULL,
  class_name TEXT NOT NULL,
  start_time TEXT NOT NULL,
  start_x    INTEGER,
  start_y    INTEGER,
  start_w    INTEGER,
  start_h    INTEGER,
  clip_name  TEXT NOT NULL,
  clip_path  TEXT NOT NULL,
  FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

CREATE INDEX idx_jobs_status   ON jobs(status);
CREATE INDEX idx_jobs_progress ON jobs(progress);
CREATE INDEX idx_clips_job_id  ON clips(job_id);
