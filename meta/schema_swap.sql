
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

