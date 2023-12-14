# export string for init script

import sqlite3
from datetime import datetime

init_query = """
/* SQLITE 3 Music Streaming App */


DROP TABLE IF EXISTS "playlistSongs";
DROP TABLE IF EXISTS "playlistData";
DROP TABLE IF EXISTS "songComments";
DROP TABLE IF EXISTS "songPlays";
DROP TABLE IF EXISTS "songLikes";
DROP TABLE IF EXISTS "songArtists";
DROP TABLE IF EXISTS "songData";
DROP TABLE IF EXISTS "albumLikes";
DROP TABLE IF EXISTS "albumData";
DROP TABLE IF EXISTS "genreData";
DROP TABLE IF EXISTS "userData";
DROP TABLE IF EXISTS "userRole";

CREATE TABLE IF NOT EXISTS "userRole" (
    "roleId" INTEGER PRIMARY KEY AUTOINCREMENT,
    "roleName" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "userData" (
    "userId" INTEGER PRIMARY KEY AUTOINCREMENT,
    "userName" TEXT NOT NULL,
    "userEmail" TEXT NOT NULL UNIQUE,
    "userPassword" TEXT NOT NULL,
    "userRoleId" INTEGER NOT NULL,
    "userDob" TEXT NOT NULL,
    "userGender" TEXT NOT NULL,
    "accountStatus" TEXT NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("userRoleId") REFERENCES "userRole" ("roleId"),
    CHECK ("accountStatus" IN ("0", "1", "2", "3")),
    CHECK ("userGender" IN ("M", "F", "O"))
);

CREATE TABLE IF NOT EXISTS "genreData" (
    "genreId" INTEGER PRIMARY KEY AUTOINCREMENT,
    "genreName" TEXT NOT NULL UNIQUE,
    "genreDescription" TEXT NULL,
    "isActive" TEXT NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("createdBy") REFERENCES "userData" ("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData" ("userId"),
    CHECK ("isActive" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "albumData" (
    "albumId" INTEGER PRIMARY KEY AUTOINCREMENT,
    "albumName" TEXT NOT NULL,
    "albumDescription" TEXT NULL,
    "albumRating" TEXT NOT NULL,
    "releaseDate" TEXT NOT NULL,
    "isActive" TEXT NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("createdBy") REFERENCES "userData" ("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData" ("userId"),
    CHECK ("albumRating" IN ("0", "1", "2", "3", "4", "5")),
    CHECK ("isActive" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "albumLikes" (
    "albumId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "isLike" TEXT NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("albumId", "userId"),
    FOREIGN KEY ("albumId") REFERENCES "albumData" ("albumId"),
    FOREIGN KEY ("userId") REFERENCES "userData" ("userId"),
    CHECK ("isLike" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "songData" (
    "songId" INTEGER PRIMARY KEY AUTOINCREMENT,
    "songName" TEXT NOT NULL,
    "songDescription" TEXT NULL,
    "songRating" TEXT NOT NULL,
    "songLyrics" TEXT NULL,
    "songDuration" TEXT NOT NULL,
    "songReleaseDate" TEXT NOT NULL,
    "songGenreId" INTEGER NOT NULL,
    "songAlbumId" INTEGER NULL,
    "isActive" TEXT NOT NULL,
    "createdBy" INTEGER NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedBy" INTEGER NULL,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("songGenreId") REFERENCES "genreData" ("genreId"),
    FOREIGN KEY ("songAlbumId") REFERENCES "albumData" ("albumId"),
    FOREIGN KEY ("createdBy") REFERENCES "userData" ("userId"),
    FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData" ("userId"),
    CHECK ("songRating" IN ("0", "1", "2", "3", "4", "5")),
    CHECK ("isActive" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "songArtists" (
    "songId" INTEGER NOT NULL,
    "artistId" INTEGER NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("songId", "artistId"),
    FOREIGN KEY ("songId") REFERENCES "songData" ("songId"),
    FOREIGN KEY ("artistId") REFERENCES "userData" ("userId")
);

CREATE TABLE IF NOT EXISTS "songLikes" (
    "songId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "isLike" TEXT NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("songId", "userId"),
    FOREIGN KEY ("songId") REFERENCES "songData" ("songId"),
    FOREIGN KEY ("userId") REFERENCES "userData" ("userId"),
    CHECK ("isLike" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "songPlays" (
    "songId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "playCount" INTEGER NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("songId", "userId"),
    FOREIGN KEY ("songId") REFERENCES "songData" ("songId"),
    FOREIGN KEY ("userId") REFERENCES "userData" ("userId")
);

CREATE TABLE IF NOT EXISTS "songComments" (
    "songId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "comment" TEXT NOT NULL,
    "redFlagCount" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("songId", "userId"),
    FOREIGN KEY ("songId") REFERENCES "songData" ("songId"),
    FOREIGN KEY ("userId") REFERENCES "userData" ("userId"),
    CHECK ("isFlagged" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "playlistData" (
    "playlistId" INTEGER PRIMARY KEY AUTOINCREMENT,
    "playlistName" TEXT NOT NULL,
    "playlistDescription" TEXT NULL,
    "userId" INTEGER NOT NULL,
    "isPublic" TEXT NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedAt" TEXT NULL,
    FOREIGN KEY ("userId") REFERENCES "userData" ("userId"),
    CHECK ("isPublic" IN ("0", "1"))
);

CREATE TABLE IF NOT EXISTS "playlistSongs" (
    "playlistId" INTEGER NOT NULL,
    "songId" INTEGER NOT NULL,
    "createdAt" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("playlistId") REFERENCES "playlistData" ("playlistId"),
    FOREIGN KEY ("songId") REFERENCES "songData" ("songId"),
    PRIMARY KEY ("playlistId", "songId")
);

INSERT INTO "userRole" ("roleName") VALUES ("ADMIN");
INSERT INTO "userRole" ("roleName") VALUES ("CREATOR");
INSERT INTO "userRole" ("roleName") VALUES ("USER");

INSERT INTO "userData" ("userName", "userEmail", "userPassword", "userRoleId", "userDob", "userGender", "accountStatus") VALUES ("Ramamurthy", "ram@gmail.com", "ram12345", "0", "1999-01-01", "M", "1");
"""

def reinitializeDatabase():
    try:
        db_connection = sqlite3.connect('./schema/app_data.db')
        db_cursor = db_connection.cursor()
        db_cursor.executescript(init_query)
        db_connection.commit()
        db_connection.close()

        print("[MESSAGE]: Database reinitialized successfully.")
    except Exception as e:
        f = open("logs/errorLogs.txt", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        print("[ERROR]: Error in reinitializing database.")
    finally:
        return