-- Create Knowledge Category table
CREATE TABLE IF NOT EXISTS education_knowledgecategory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'fa-book',
    color VARCHAR(20) DEFAULT '#4e73df',
    "order" INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Create Knowledge Tag table
CREATE TABLE IF NOT EXISTS education_knowledgetag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL
);

-- Create Knowledge Article table
CREATE TABLE IF NOT EXISTS education_knowledgearticle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    summary TEXT NOT NULL,
    content TEXT NOT NULL,
    featured_image VARCHAR(100),
    is_published BOOLEAN NOT NULL,
    view_count INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    author_id INTEGER NOT NULL REFERENCES auth_user(id),
    category_id INTEGER REFERENCES education_knowledgecategory(id)
);

-- Create Media Attachment table
CREATE TABLE IF NOT EXISTS education_mediaattachment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file VARCHAR(100) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    description TEXT,
    created_at DATETIME NOT NULL,
    article_id INTEGER NOT NULL REFERENCES education_knowledgearticle(id)
);

-- Create many-to-many relationship table for articles and tags
CREATE TABLE IF NOT EXISTS education_knowledgearticle_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledgearticle_id INTEGER NOT NULL REFERENCES education_knowledgearticle(id),
    knowledgetag_id INTEGER NOT NULL REFERENCES education_knowledgetag(id),
    UNIQUE(knowledgearticle_id, knowledgetag_id)
);

-- Add migration record
INSERT OR IGNORE INTO django_migrations (app, name, applied) 
VALUES ('education', '0001_initial', datetime('now'));
