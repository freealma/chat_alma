--
-- PostgreSQL database dump
--

\restrict d3khuO3krgN2tVHfYA1IvymFcFTZW89fLiUAJY93u9Zs6scGnJ7PvWvxRymeX0g

-- Dumped from database version 15.4 (Debian 15.4-2.pgdg120+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-0+deb12u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: alma; Type: SCHEMA; Schema: -; Owner: alma
--

CREATE SCHEMA alma;


ALTER SCHEMA alma OWNER TO alma;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alma_memories; Type: TABLE; Schema: alma; Owner: alma
--

CREATE TABLE alma.alma_memories (
    id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    memory_type character varying(50) NOT NULL,
    content text NOT NULL,
    metadata jsonb,
    context text,
    importance integer DEFAULT 1
);


ALTER TABLE alma.alma_memories OWNER TO alma;

--
-- Name: alma_memories_id_seq; Type: SEQUENCE; Schema: alma; Owner: alma
--

CREATE SEQUENCE alma.alma_memories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alma.alma_memories_id_seq OWNER TO alma;

--
-- Name: alma_memories_id_seq; Type: SEQUENCE OWNED BY; Schema: alma; Owner: alma
--

ALTER SEQUENCE alma.alma_memories_id_seq OWNED BY alma.alma_memories.id;


--
-- Name: pentest_sessions; Type: TABLE; Schema: alma; Owner: alma
--

CREATE TABLE alma.pentest_sessions (
    id integer NOT NULL,
    session_name character varying(255) NOT NULL,
    target text,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(50) DEFAULT 'active'::character varying,
    findings jsonb
);


ALTER TABLE alma.pentest_sessions OWNER TO alma;

--
-- Name: pentest_sessions_id_seq; Type: SEQUENCE; Schema: alma; Owner: alma
--

CREATE SEQUENCE alma.pentest_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alma.pentest_sessions_id_seq OWNER TO alma;

--
-- Name: pentest_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: alma; Owner: alma
--

ALTER SEQUENCE alma.pentest_sessions_id_seq OWNED BY alma.pentest_sessions.id;


--
-- Name: alma_memories id; Type: DEFAULT; Schema: alma; Owner: alma
--

ALTER TABLE ONLY alma.alma_memories ALTER COLUMN id SET DEFAULT nextval('alma.alma_memories_id_seq'::regclass);


--
-- Name: pentest_sessions id; Type: DEFAULT; Schema: alma; Owner: alma
--

ALTER TABLE ONLY alma.pentest_sessions ALTER COLUMN id SET DEFAULT nextval('alma.pentest_sessions_id_seq'::regclass);


--
-- Name: alma_memories alma_memories_pkey; Type: CONSTRAINT; Schema: alma; Owner: alma
--

ALTER TABLE ONLY alma.alma_memories
    ADD CONSTRAINT alma_memories_pkey PRIMARY KEY (id);


--
-- Name: pentest_sessions pentest_sessions_pkey; Type: CONSTRAINT; Schema: alma; Owner: alma
--

ALTER TABLE ONLY alma.pentest_sessions
    ADD CONSTRAINT pentest_sessions_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict d3khuO3krgN2tVHfYA1IvymFcFTZW89fLiUAJY93u9Zs6scGnJ7PvWvxRymeX0g

