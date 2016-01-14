-- Table: newsarticles_article_categories

-- DROP TABLE newsarticles_article_categories;

CREATE TABLE newsarticles_article_categories
(
  id serial NOT NULL,
  article_id integer NOT NULL,
  category_id integer NOT NULL,
  CONSTRAINT newsarticles_article_categories_pkey PRIMARY KEY (id),
  CONSTRAINT article_id_refs_id_4f17e19f FOREIGN KEY (article_id)
      REFERENCES newsarticles_article (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT newsarticles_article_categories_category_id_fkey FOREIGN KEY (category_id)
      REFERENCES newsarticles_category (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT newsarticles_article_categories_article_id_key UNIQUE (article_id, category_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE newsarticles_article_categories OWNER TO cjpuser;

-- Index: newsarticles_article_categories_article_id

-- DROP INDEX newsarticles_article_categories_article_id;

CREATE INDEX newsarticles_article_categories_article_id
  ON newsarticles_article_categories
  USING btree
  (article_id);

-- Index: newsarticles_article_categories_category_id

-- DROP INDEX newsarticles_article_categories_category_id;

CREATE INDEX newsarticles_article_categories_category_id
  ON newsarticles_article_categories
  USING btree
  (category_id);

-- Index: newsarticles_article_created

-- DROP INDEX newsarticles_article_created;

CREATE INDEX newsarticles_article_created
  ON newsarticles_article
    USING btree
      (created);
