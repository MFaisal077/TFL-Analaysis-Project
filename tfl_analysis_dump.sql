--
-- PostgreSQL database dump
--

\restrict awQyxoxbjlXOM3IhkgZszVYRUsxIQ2l5osOvNTSiiAHHhPZ0IpcqwOTKq944Vbl

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: css; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.css (
    line character varying(100) NOT NULL,
    year character varying(10) NOT NULL,
    customer_satisfaction numeric
);


ALTER TABLE public.css OWNER TO postgres;

--
-- Name: esc_avl; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.esc_avl (
    line character varying(100) NOT NULL,
    year character varying(10) NOT NULL,
    esc_avail numeric
);


ALTER TABLE public.esc_avl OWNER TO postgres;

--
-- Name: excess_journey_time; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.excess_journey_time (
    line character varying(100) NOT NULL,
    year character varying(10) NOT NULL,
    ejt numeric
);


ALTER TABLE public.excess_journey_time OWNER TO postgres;

--
-- Name: lchbycategory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lchbycategory (
    category character varying(100) NOT NULL,
    year character varying(10) NOT NULL,
    lost_customer_hours numeric
);


ALTER TABLE public.lchbycategory OWNER TO postgres;

--
-- Name: lchbyline; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lchbyline (
    line character varying(100) NOT NULL,
    year character varying(10) NOT NULL,
    lost_customer_hours numeric
);


ALTER TABLE public.lchbyline OWNER TO postgres;

--
-- Name: schedule_operated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_operated (
    line character varying(200),
    year character varying(200),
    schedule_operated numeric
);


ALTER TABLE public.schedule_operated OWNER TO postgres;

--
-- Name: v_perfomance_base; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_perfomance_base AS
 SELECT l.line,
    l.year,
    l.lost_customer_hours,
    e.ejt,
    c.customer_satisfaction,
    esc.esc_avail,
    sch.schedule_operated
   FROM ((((public.lchbyline l
     LEFT JOIN public.excess_journey_time e ON ((((l.line)::text = (e.line)::text) AND ((l.year)::text = (e.year)::text))))
     LEFT JOIN public.css c ON ((((l.line)::text = (c.line)::text) AND ((l.year)::text = (c.year)::text))))
     LEFT JOIN public.esc_avl esc ON ((((l.line)::text = (esc.line)::text) AND ((l.year)::text = (esc.year)::text))))
     LEFT JOIN public.schedule_operated sch ON ((((l.line)::text = (sch.line)::text) AND ((l.year)::text = (sch.year)::text))));


ALTER VIEW public.v_perfomance_base OWNER TO postgres;

--
-- Name: v_analytics; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_analytics AS
 SELECT line,
    year,
    lost_customer_hours,
    lag(lost_customer_hours, 1) OVER (PARTITION BY line ORDER BY year) AS previous_year_lch,
    round((((lost_customer_hours - lag(lost_customer_hours, 1) OVER (PARTITION BY line ORDER BY year)) / NULLIF(lag(lost_customer_hours, 1) OVER (PARTITION BY line ORDER BY year), (0)::numeric)) * (100)::numeric), 2) AS yoy_change
   FROM public.v_perfomance_base;


ALTER VIEW public.v_analytics OWNER TO postgres;

--
-- Name: v_anomaly_flags; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_anomaly_flags AS
 WITH stats AS (
         SELECT v_analytics.line,
            avg(v_analytics.yoy_change) AS mean_yoy,
            stddev_samp(v_analytics.yoy_change) AS std_yoy
           FROM public.v_analytics
          GROUP BY v_analytics.line
        )
 SELECT a.line,
    a.year,
    a.lost_customer_hours,
    a.previous_year_lch,
    a.yoy_change,
    round(s.mean_yoy, 2) AS mean_yoy,
    round(s.std_yoy, 2) AS std_yoy,
    round(((a.yoy_change - s.mean_yoy) / NULLIF(s.std_yoy, (0)::numeric)), 2) AS z_score,
        CASE
            WHEN (abs(((a.yoy_change - s.mean_yoy) / NULLIF(s.std_yoy, (0)::numeric))) >= (2)::numeric) THEN 'Anomaly'::text
            ELSE 'Normal'::text
        END AS anomaly_flag
   FROM (public.v_analytics a
     LEFT JOIN stats s ON (((a.line)::text = (s.line)::text)))
  ORDER BY a.line, a.year;


ALTER VIEW public.v_anomaly_flags OWNER TO postgres;

--
-- Name: v_yearly_rankings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_yearly_rankings AS
 SELECT a.line,
    a.year,
    a.lost_customer_hours,
    a.schedule_operated,
    a.customer_satisfaction,
    a.esc_avail,
    a.ejt,
    b.yoy_change,
    dense_rank() OVER (PARTITION BY a.year ORDER BY a.lost_customer_hours) AS rank_lch_best,
    dense_rank() OVER (PARTITION BY a.year ORDER BY a.schedule_operated DESC NULLS LAST) AS rank_schedule_best,
    dense_rank() OVER (PARTITION BY a.year ORDER BY a.customer_satisfaction DESC NULLS LAST) AS rank_css_best
   FROM (public.v_perfomance_base a
     LEFT JOIN public.v_analytics b ON ((((a.line)::text = (b.line)::text) AND ((a.year)::text = (b.year)::text))));


ALTER VIEW public.v_yearly_rankings OWNER TO postgres;

--
-- Name: v_correlation_base; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_correlation_base AS
 SELECT line,
    year,
    lost_customer_hours,
    schedule_operated,
    customer_satisfaction,
    esc_avail,
    ejt,
    yoy_change
   FROM public.v_yearly_rankings
  WHERE ((schedule_operated IS NOT NULL) OR (customer_satisfaction IS NOT NULL) OR (esc_avail IS NOT NULL) OR (ejt IS NOT NULL))
  ORDER BY line, year;


ALTER VIEW public.v_correlation_base OWNER TO postgres;

--
-- Name: v_data_quality_report; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_data_quality_report AS
 SELECT line,
    count(*) AS years_total,
    count(ejt) AS years_with_ejt,
    count(customer_satisfaction) AS years_with_css,
    count(schedule_operated) AS years_with_schedule,
    count(esc_avail) AS years_with_esc,
    (count(*) - count(ejt)) AS missing_ejt_years,
    (count(*) - count(customer_satisfaction)) AS missing_css_years,
    (count(*) - count(schedule_operated)) AS missing_schedule_years,
    (count(*) - count(esc_avail)) AS missing_esc_years,
    sum(
        CASE
            WHEN (esc_avail = (0)::numeric) THEN 1
            ELSE 0
        END) AS esc_zero_years
   FROM public.v_perfomance_base
  GROUP BY line
  ORDER BY (count(*) - count(ejt)) DESC, (count(*) - count(customer_satisfaction)) DESC;


ALTER VIEW public.v_data_quality_report OWNER TO postgres;

--
-- Name: v_lch_category_contribution; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_lch_category_contribution AS
 WITH yearly_total AS (
         SELECT lchbycategory.year,
            sum(lchbycategory.lost_customer_hours) AS total_lch
           FROM public.lchbycategory
          GROUP BY lchbycategory.year
        )
 SELECT c.year,
    c.category,
    c.lost_customer_hours,
    round(((c.lost_customer_hours / NULLIF(t.total_lch, (0)::numeric)) * (100)::numeric), 2) AS percent_contribution
   FROM (public.lchbycategory c
     JOIN yearly_total t ON (((c.year)::text = (t.year)::text)))
  ORDER BY c.year, (round(((c.lost_customer_hours / NULLIF(t.total_lch, (0)::numeric)) * (100)::numeric), 2)) DESC;


ALTER VIEW public.v_lch_category_contribution OWNER TO postgres;

--
-- Name: v_lch_yoy; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_lch_yoy AS
 SELECT year,
    line,
    lost_customer_hours,
    lag(lost_customer_hours) OVER (PARTITION BY line ORDER BY year) AS prev_year_lch,
    COALESCE((lost_customer_hours - lag(lost_customer_hours) OVER (PARTITION BY line ORDER BY year)), (0)::numeric) AS yoy_change
   FROM public.lchbyline
  ORDER BY line, year;


ALTER VIEW public.v_lch_yoy OWNER TO postgres;

--
-- Name: v_line_volatility; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_line_volatility AS
 SELECT line,
    stddev_samp(yoy_change) AS stddev_samp,
    avg(yoy_change) AS avg_trend,
    min(yoy_change) AS worst_drop,
    max(yoy_change) AS biggest_spike,
    count(yoy_change) AS valid_years
   FROM public.v_analytics
  GROUP BY line;


ALTER VIEW public.v_line_volatility OWNER TO postgres;

--
-- Name: v_line_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_line_summary AS
 SELECT b.line,
    round(avg(b.lost_customer_hours), 2) AS avg_lch,
    round(avg(b.schedule_operated), 2) AS avg_schedule_operated,
    round(avg(b.customer_satisfaction), 2) AS avg_customer_satisfaction,
    round(avg(b.esc_avail), 2) AS avg_esc_avail,
    round(avg(b.ejt), 2) AS avg_ejt,
    count(*) AS years_total,
    count(b.ejt) AS years_with_ejt,
    count(b.schedule_operated) AS years_with_schedule,
    count(b.customer_satisfaction) AS years_with_css,
    count(b.esc_avail) AS years_with_esc,
    round(v.stddev_samp, 2) AS volatility,
    round(v.avg_trend, 2) AS avg_trend,
    round(v.worst_drop, 2) AS worst_drop,
    round(v.biggest_spike, 2) AS biggest_spike,
    v.valid_years
   FROM (public.v_perfomance_base b
     LEFT JOIN public.v_line_volatility v ON (((b.line)::text = (v.line)::text)))
  GROUP BY b.line, v.stddev_samp, v.avg_trend, v.worst_drop, v.biggest_spike, v.valid_years
  ORDER BY (round(v.stddev_samp, 2)) DESC;


ALTER VIEW public.v_line_summary OWNER TO postgres;

--
-- Name: v_line_trend_classification; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_line_trend_classification AS
 SELECT line,
    round(avg(yoy_change), 2) AS avg_yoy_change,
    round(min(yoy_change), 2) AS worst_yoy_change,
    round(max(yoy_change), 2) AS best_yoy_change,
    count(yoy_change) AS valid_years,
        CASE
            WHEN (avg(yoy_change) > (5)::numeric) THEN 'Improving'::text
            WHEN (avg(yoy_change) < ('-5'::integer)::numeric) THEN 'Declining'::text
            ELSE 'Stable'::text
        END AS trend_classification
   FROM public.v_analytics
  GROUP BY line
  ORDER BY (round(avg(yoy_change), 2)) DESC;


ALTER VIEW public.v_line_trend_classification OWNER TO postgres;

--
-- Name: v_network_benchmark; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_network_benchmark AS
 WITH yearly_network_avg AS (
         SELECT v_perfomance_base.year,
            avg(v_perfomance_base.lost_customer_hours) AS network_avg_lch,
            avg(v_perfomance_base.schedule_operated) AS network_avg_schedule,
            avg(v_perfomance_base.customer_satisfaction) AS network_avg_css,
            avg(v_perfomance_base.esc_avail) AS network_avg_esc,
            avg(v_perfomance_base.ejt) AS network_avg_ejt
           FROM public.v_perfomance_base
          GROUP BY v_perfomance_base.year
        )
 SELECT b.line,
    b.year,
    b.lost_customer_hours,
    b.schedule_operated,
    b.customer_satisfaction,
    b.esc_avail,
    b.ejt,
    round(n.network_avg_lch, 2) AS network_avg_lch,
    round(n.network_avg_schedule, 2) AS network_avg_schedule,
    round(n.network_avg_css, 2) AS network_avg_css,
    round(n.network_avg_esc, 2) AS network_avg_esc,
    round(n.network_avg_ejt, 2) AS network_avg_ejt,
    round((b.lost_customer_hours - n.network_avg_lch), 2) AS lch_vs_network,
    round((b.schedule_operated - n.network_avg_schedule), 2) AS schedule_vs_network,
    round((b.customer_satisfaction - n.network_avg_css), 2) AS css_vs_network,
    round((b.esc_avail - n.network_avg_esc), 2) AS esc_vs_network,
    round((b.ejt - n.network_avg_ejt), 2) AS ejt_vs_network
   FROM (public.v_perfomance_base b
     LEFT JOIN yearly_network_avg n ON (((b.year)::text = (n.year)::text)))
  ORDER BY b.year, b.line;


ALTER VIEW public.v_network_benchmark OWNER TO postgres;

--
-- Data for Name: css; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.css (line, year, customer_satisfaction) FROM stdin;
Bakerloo	2004/05	79
Central	2004/05	78
District	2004/05	79
Jubilee	2004/05	78
Circle + H&C	2004/05	76
Metropolitan	2004/05	76
Northern	2004/05	75
Piccadilly	2004/05	80
Victoria	2004/05	76
Network	2004/05	78
Bakerloo	2005/06	80
Central	2005/06	78
District	2005/06	77
Jubilee	2005/06	78
Circle + H&C	2005/06	77
Metropolitan	2005/06	73
Northern	2005/06	79
Piccadilly	2005/06	80
Victoria	2005/06	78
Network	2005/06	78
Bakerloo	2006/07	79
Central	2006/07	78
District	2006/07	74
Jubilee	2006/07	79
Circle + H&C	2006/07	74
Metropolitan	2006/07	77
Northern	2006/07	74
Piccadilly	2006/07	77
Victoria	2006/07	76
Network	2006/07	76
Bakerloo	2007/08	79
Central	2007/08	77
District	2007/08	77
Jubilee	2007/08	78
Circle + H&C	2007/08	76
Metropolitan	2007/08	78
Northern	2007/08	77
Piccadilly	2007/08	77
Victoria	2007/08	74
Network	2007/08	77
Bakerloo	2008/09	80
Central	2008/09	80
District	2008/09	79
Jubilee	2008/09	80
Circle + H&C	2008/09	77
Metropolitan	2008/09	77
Northern	2008/09	81
Piccadilly	2008/09	80
Victoria	2008/09	78
Network	2008/09	79
Bakerloo	2009/10	80
Central	2009/10	80
District	2009/10	79
Jubilee	2009/10	80
Circle + H&C	2009/10	77
Metropolitan	2009/10	78
Northern	2009/10	79
Piccadilly	2009/10	80
Victoria	2009/10	79
Network	2009/10	79
Bakerloo	2010/11	81
Central	2010/11	79
District	2010/11	79
Jubilee	2010/11	79
Circle + H&C	2010/11	78
Metropolitan	2010/11	78
Northern	2010/11	80
Piccadilly	2010/11	80
Victoria	2010/11	79
Network	2010/11	79
Bakerloo	2011/12	84
Central	2011/12	80
District	2011/12	78
Jubilee	2011/12	81
Circle + H&C	2011/12	79
Metropolitan	2011/12	80
Northern	2011/12	80
Piccadilly	2011/12	80
Victoria	2011/12	79
Network	2011/12	80
Bakerloo	2012/13	83
Central	2012/13	82
District	2012/13	83
Jubilee	2012/13	85
Circle + H&C	2012/13	82
Metropolitan	2012/13	84
Northern	2012/13	83
Piccadilly	2012/13	84
Victoria	2012/13	84
Network	2012/13	83
Bakerloo	2013/14	83
Central	2013/14	82
District	2013/14	83
Jubilee	2013/14	84
Circle + H&C	2013/14	83
Metropolitan	2013/14	84
Northern	2013/14	82
Piccadilly	2013/14	82
Victoria	2013/14	83
Network	2013/14	83
Bakerloo	2014/15	85
Central	2014/15	83
District	2014/15	83
Jubilee	2014/15	86
Circle + H&C	2014/15	84
Metropolitan	2014/15	88
Northern	2014/15	85
Piccadilly	2014/15	84
Victoria	2014/15	84
Network	2014/15	84
Bakerloo	2015/16	86
Central	2015/16	83
District	2015/16	86
Jubilee	2015/16	87
Circle + H&C	2015/16	85
Metropolitan	2015/16	87
Northern	2015/16	85
Piccadilly	2015/16	85
Victoria	2015/16	85
Network	2015/16	85
Bakerloo	2016/17	85
Central	2016/17	84
District	2016/17	86
Jubilee	2016/17	87
Circle + H&C	2016/17	85
Metropolitan	2016/17	87
Northern	2016/17	84
Piccadilly	2016/17	85
Victoria	2016/17	85
Network	2016/17	85
\.


--
-- Data for Name: esc_avl; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.esc_avl (line, year, esc_avail) FROM stdin;
Bakerloo	2004/05	95.00
Central	2004/05	94.50
Waterloo & City	2004/05	0.00
Circle & Ham	2004/05	89.20
District	2004/05	87.70
Jubilee	2004/05	98.00
Metropolitan	2004/05	99.50
Northern	2004/05	89.60
Piccadilly	2004/05	94.20
Victoria	2004/05	90.30
Bakerloo	2005/06	97.10
Central	2005/06	94.90
Waterloo & City	2005/06	0.00
Circle & Ham	2005/06	93.70
District	2005/06	98.90
Jubilee	2005/06	96.70
Metropolitan	2005/06	98.40
Northern	2005/06	93.60
Piccadilly	2005/06	96.90
Victoria	2005/06	93.70
Bakerloo	2006/07	98.30
Central	2006/07	97.40
Waterloo & City	2006/07	0.00
Circle & Ham	2006/07	96.40
District	2006/07	95.50
Jubilee	2006/07	95.50
Metropolitan	2006/07	98.60
Northern	2006/07	95.90
Piccadilly	2006/07	95.80
Victoria	2006/07	97.50
Bakerloo	2007/08	95.40
Central	2007/08	96.00
Waterloo & City	2007/08	0.00
Circle & Ham	2007/08	97.80
District	2007/08	94.20
Jubilee	2007/08	95.90
Metropolitan	2007/08	99.80
Northern	2007/08	94.50
Piccadilly	2007/08	96.60
Victoria	2007/08	98.20
Bakerloo	2008/09	95.60
Central	2008/09	89.70
Waterloo & City	2008/09	0.00
Circle & Ham	2008/09	96.90
District	2008/09	99.80
Jubilee	2008/09	96.20
Metropolitan	2008/09	99.60
Northern	2008/09	98.90
Piccadilly	2008/09	95.10
Victoria	2008/09	97.50
Bakerloo	2009/10	95.60
Central	2009/10	92.70
Waterloo & City	2009/10	0.00
Circle & Ham	2009/10	96.00
District	2009/10	97.40
Jubilee	2009/10	97.10
Metropolitan	2009/10	99.80
Northern	2009/10	98.00
Piccadilly	2009/10	94.20
Victoria	2009/10	95.80
Bakerloo	2010/11	89.20
Central	2010/11	95.20
Waterloo & City	2010/11	0.00
Circle & Ham	2010/11	98.00
District	2010/11	96.70
Jubilee	2010/11	96.60
Metropolitan	2010/11	99.70
Northern	2010/11	98.20
Piccadilly	2010/11	92.90
Victoria	2010/11	96.60
Bakerloo	2011/12	91.90
Central	2011/12	93.50
Waterloo & City	2011/12	0.00
Circle & Ham	2011/12	97.80
District	2011/12	98.20
Jubilee	2011/12	96.40
Metropolitan	2011/12	98.50
Northern	2011/12	97.30
Piccadilly	2011/12	95.70
Victoria	2011/12	97.10
Bakerloo	2012/13	99.10
Central	2012/13	97.90
Waterloo & City	2012/13	0.00
Circle & Ham	2012/13	98.90
District	2012/13	99.30
Jubilee	2012/13	97.10
Metropolitan	2012/13	86.90
Northern	2012/13	97.30
Piccadilly	2012/13	97.30
Victoria	2012/13	97.80
Bakerloo	2013/14	98.70
Central	2013/14	96.00
Waterloo & City	2013/14	0.00
Circle & Ham	2013/14	98.40
District	2013/14	92.60
Jubilee	2013/14	97.30
Metropolitan	2013/14	99.90
Northern	2013/14	97.70
Piccadilly	2013/14	97.90
Victoria	2013/14	95.10
Bakerloo	2014/15	99.40
Central	2014/15	95.50
Waterloo & City	2014/15	0.00
Circle & Ham	2014/15	95.60
District	2014/15	87.80
Jubilee	2014/15	97.20
Metropolitan	2014/15	98.90
Northern	2014/15	97.20
Piccadilly	2014/15	96.40
Victoria	2014/15	97.40
Bakerloo	2015/16	99.70
Central	2015/16	99.30
Waterloo & City	2015/16	0.00
Circle & Ham	2015/16	95.10
District	2015/16	99.60
Jubilee	2015/16	96.90
Metropolitan	2015/16	99.80
Northern	2015/16	97.70
Piccadilly	2015/16	98.20
Victoria	2015/16	96.70
Bakerloo	2016/17	99.40
Central	2016/17	96.30
Waterloo & City	2016/17	0.00
Circle & Ham	2016/17	97.40
District	2016/17	99.80
Jubilee	2016/17	97.10
Metropolitan	2016/17	98.60
Northern	2016/17	98.40
Piccadilly	2016/17	97.50
Victoria	2016/17	99.40
\.


--
-- Data for Name: excess_journey_time; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.excess_journey_time (line, year, ejt) FROM stdin;
Bakerloo	2010/11	5.56
Central	2010/11	6.01
Waterloo & City	2010/11	2.19
Circle & Ham	2010/11	5.67
District	2010/11	5.06
Jubilee	2010/11	6.94
Metropolitan	2010/11	6.25
Northern	2010/11	4.07
Piccadilly	2010/11	5.26
Victoria	2010/11	5.61
Bakerloo	2011/12	4.07
Central	2011/12	5.74
Waterloo & City	2011/12	1.78
Circle & Ham	2011/12	4.58
District	2011/12	4.41
Jubilee	2011/12	4.26
Metropolitan	2011/12	4.7
Northern	2011/12	3.6
Piccadilly	2011/12	4.82
Victoria	2011/12	4.53
Bakerloo	2012/13	4.16
Central	2012/13	4.78
Waterloo & City	2012/13	1.79
Circle & Ham	2012/13	4.85
District	2012/13	4.27
Jubilee	2012/13	3.67
Metropolitan	2012/13	4.41
Northern	2012/13	3.58
Piccadilly	2012/13	4.21
Victoria	2012/13	3.71
Bakerloo	2013/14	3.52
Central	2013/14	4.78
Waterloo & City	2013/14	2.04
Circle & Ham	2013/14	5.44
District	2013/14	4.15
Jubilee	2013/14	3.62
Metropolitan	2013/14	4.38
Northern	2013/14	3.68
Piccadilly	2013/14	4.0
Victoria	2013/14	3.8
Bakerloo	2014/15	3.65
Central	2014/15	4.31
Waterloo & City	2014/15	2.06
Circle & Ham	2014/15	4.89
District	2014/15	4.06
Jubilee	2014/15	2.85
Metropolitan	2014/15	3.2
Northern	2014/15	3.28
Piccadilly	2014/15	3.94
Victoria	2014/15	3.19
Bakerloo	2015/16	3.68
Central	2015/16	4.4
Waterloo & City	2015/16	2.07
Circle & Ham	2015/16	5.69
District	2015/16	4.19
Jubilee	2015/16	3.12
Metropolitan	2015/16	4.1
Northern	2015/16	2.83
Piccadilly	2015/16	4.12
Victoria	2015/16	3.0
Bakerloo	2016/17	3.58
Central	2016/17	4.46
Waterloo & City	2016/17	2.19
Circle & Ham	2016/17	5.13
District	2016/17	4.33
Jubilee	2016/17	2.72
Metropolitan	2016/17	6.33
Northern	2016/17	2.46
Piccadilly	2016/17	4.44
Victoria	2016/17	3.02
\.


--
-- Data for Name: lchbycategory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lchbycategory (category, year, lost_customer_hours) FROM stdin;
Animals / Pests	2004/05	1603
ATP / ATO	2004/05	55090
Bridge Strike	2004/05	1867
Customers & Public	2004/05	370474
External Properties	2004/05	1536
Fleet	2004/05	810549
Gas / Water / Sewage	2004/05	12489
National Rail Operations	2004/05	42899
Other LU Operations	2004/05	18900
Power Failure	2004/05	11466
Safety & Security	2004/05	112441
Signals	2004/05	841022
Staff	2004/05	260428
Staff - Absence or Shortage	2004/05	225892
Staff Industrial Action	2004/05	185797
Stations	2004/05	164506
Track & Civils	2004/05	293846
Transplant Operations	2004/05	13575
Other	2004/05	130
Vandalism	2004/05	24388
Weather	2004/05	990
TOTAL	2004/05	3449886
Animals / Pests	2005/06	318
ATP / ATO	2005/06	15561
Bridge Strike	2005/06	798
Customers & Public	2005/06	342168
External Properties	2005/06	7681
Fleet	2005/06	786762
Gas / Water / Sewage	2005/06	1646
National Rail Operations	2005/06	34473
Other LU Operations	2005/06	12680
Power Failure	2005/06	15720
Safety & Security	2005/06	1238803
Signals	2005/06	624380
Staff	2005/06	474811
Staff - Absence or Shortage	2005/06	248185
Staff Industrial Action	2005/06	262431
Stations	2005/06	238289
Track & Civils	2005/06	467775
Transplant Operations	2005/06	907
Other	2005/06	1939
Vandalism	2005/06	53696
Weather	2005/06	4594
TOTAL	2005/06	4833617
Animals / Pests	2006/07	1554
ATP / ATO	2006/07	11927
Bridge Strike	2006/07	501
Customers & Public	2006/07	422408
External Properties	2006/07	2894
Fleet	2006/07	827643
Gas / Water / Sewage	2006/07	11448
National Rail Operations	2006/07	28036
Other LU Operations	2006/07	11213
Power Failure	2006/07	14835
Safety & Security	2006/07	77421
Signals	2006/07	642461
Staff	2006/07	360768
Staff - Absence or Shortage	2006/07	255581
Staff Industrial Action	2006/07	19696
Stations	2006/07	169041
Track & Civils	2006/07	585465
Transplant Operations	2006/07	1067
Other	2006/07	1088
Vandalism	2006/07	40965
Weather	2006/07	26901
TOTAL	2006/07	3512910
Animals / Pests	2007/08	1322
ATP / ATO	2007/08	8829
Bridge Strike	2007/08	513
Customers & Public	2007/08	418575
External Properties	2007/08	9355
Fleet	2007/08	1068261
Gas / Water / Sewage	2007/08	3196
National Rail Operations	2007/08	32637
Other LU Operations	2007/08	16562
Power Failure	2007/08	7913
Safety & Security	2007/08	57477
Signals	2007/08	608837
Staff	2007/08	454134
Staff - Absence or Shortage	2007/08	281268
Staff Industrial Action	2007/08	5492
Stations	2007/08	145882
Track & Civils	2007/08	589439
Transplant Operations	2007/08	784
Other	2007/08	133
Vandalism	2007/08	52362
Weather	2007/08	10709
TOTAL	2007/08	3773681
Animals / Pests	2008/09	1711
ATP / ATO	2008/09	10781
Bridge Strike	2008/09	1136
Customers & Public	2008/09	398729
External Properties	2008/09	3853
Fleet	2008/09	695777
Gas / Water / Sewage	2008/09	4498
National Rail Operations	2008/09	18665
Other LU Operations	2008/09	12673
Power Failure	2008/09	7614
Safety & Security	2008/09	52672
Signals	2008/09	511533
Staff	2008/09	315016
Staff - Absence or Shortage	2008/09	164096
Staff Industrial Action	2008/09	176
Stations	2008/09	114006
Track & Civils	2008/09	323404
Transplant Operations	2008/09	165
Other	2008/09	170
Vandalism	2008/09	42011
Weather	2008/09	137924
TOTAL	2008/09	2816607
Animals / Pests	2009/10	462
ATP / ATO	2009/10	8626
Bridge Strike	2009/10	68
Customers & Public	2009/10	371203
External Properties	2009/10	2370
Fleet	2009/10	484212
Gas / Water / Sewage	2009/10	2388
National Rail Operations	2009/10	15092
Other LU Operations	2009/10	14321
Power Failure	2009/10	4957
Safety & Security	2009/10	34361
Signals	2009/10	417942
Staff	2009/10	255822
Staff - Absence or Shortage	2009/10	139261
Staff Industrial Action	2009/10	319303
Stations	2009/10	151806
Track & Civils	2009/10	277546
Transplant Operations	2009/10	88
Other	2009/10	36
Vandalism	2009/10	35633
Weather	2009/10	11918
TOTAL	2009/10	2547417
Animals / Pests	2010/11	1338
ATP / ATO	2010/11	40034
Bridge Strike	2010/11	328
Customers & Public	2010/11	370301
External Properties	2010/11	1857
Fleet	2010/11	539396
Gas / Water / Sewage	2010/11	14759
National Rail Operations	2010/11	39498
Other LU Operations	2010/11	5723
Power Failure	2010/11	16068
Safety & Security	2010/11	32272
Signals	2010/11	481831
Staff	2010/11	308335
Staff - Absence or Shortage	2010/11	137465
Staff Industrial Action	2010/11	572056
Stations	2010/11	101754
Track & Civils	2010/11	294146
Transplant Operations	2010/11	5812
Other	2010/11	14
Vandalism	2010/11	47031
Weather	2010/11	32009
TOTAL	2010/11	3042028
Animals / Pests	2011/12	1644
ATP / ATO	2011/12	16038
Bridge Strike	2011/12	2073
Customers & Public	2011/12	383968
External Properties	2011/12	5180
Fleet	2011/12	400897
Gas / Water / Sewage	2011/12	3576
National Rail Operations	2011/12	27874
Other LU Operations	2011/12	9593
Power Failure	2011/12	12893
Safety & Security	2011/12	20754
Signals	2011/12	410205
Staff	2011/12	302535
Staff - Absence or Shortage	2011/12	248816
Staff Industrial Action	2011/12	29150
Stations	2011/12	104085
Track & Civils	2011/12	173911
Transplant Operations	2011/12	40
Other	2011/12	44
Vandalism	2011/12	20261
Weather	2011/12	18862
TOTAL	2011/12	2192397
Animals / Pests	2012/13	424
ATP / ATO	2012/13	11235
Bridge Strike	2012/13	270
Customers & Public	2012/13	326046
External Properties	2012/13	9982
Fleet	2012/13	346138
Gas / Water / Sewage	2012/13	32207
National Rail Operations	2012/13	15533
Other LU Operations	2012/13	8248
Power Failure	2012/13	8658
Safety & Security	2012/13	18295
Signals	2012/13	285148
Staff	2012/13	223511
Staff - Absence or Shortage	2012/13	126896
Staff Industrial Action	2012/13	86080
Stations	2012/13	73111
Track & Civils	2012/13	165038
Transplant Operations	2012/13	132
Other	2012/13	35
Vandalism	2012/13	14081
Weather	2012/13	7199
TOTAL	2012/13	1758267
Animals / Pests	2013/14	2785
ATP / ATO	2013/14	21458
Bridge Strike	2013/14	118
Customers & Public	2013/14	328803
External Properties	2013/14	2739
Fleet	2013/14	348586
Gas / Water / Sewage	2013/14	5287
National Rail Operations	2013/14	19345
Other LU Operations	2013/14	7149
Power Failure	2013/14	7647
Safety & Security	2013/14	12606
Signals	2013/14	263993
Staff	2013/14	227513
Staff - Absence or Shortage	2013/14	133280
Staff Industrial Action	2013/14	268107
Stations	2013/14	58284
Track & Civils	2013/14	116177
Transplant Operations	2013/14	46
Other	2013/14	0
Vandalism	2013/14	10115
Weather	2013/14	29141
TOTAL	2013/14	1863178
Animals / Pests	2014/15	829
ATP / ATO	2014/15	25587
Bridge Strike	2014/15	290
Crowding	2014/15	16743
Customers & Public	2014/15	273461
External Properties	2014/15	6805
Fleet	2014/15	300911
Gas / Water / Sewage	2014/15	2500
National Rail Operations	2014/15	20916
Other LU Operations	2014/15	3117
Power Failure	2014/15	15124
Safety & Security	2014/15	12425
Signals	2014/15	251604
Staff	2014/15	202859
Staff - Absence or Shortage	2014/15	128872
Staff Industrial Action	2014/15	293971
Stations	2014/15	53004
Track & Civils	2014/15	102367
Transplant Operations	2014/15	14443
Other	2014/15	89
Vandalism	2014/15	11009
Weather	2014/15	6286
TOTAL	2014/15	1743212
Animals / Pests	2015/16	656
ATP / ATO	2015/16	21614
Bridge Strike	2015/16	326
Crowding	2015/16	30973
Customers & Public	2015/16	279545
External Properties	2015/16	8349
Fleet	2015/16	371272
Gas / Water / Sewage	2015/16	146
National Rail Operations	2015/16	20396
Other LU Operations	2015/16	5300
Power Failure	2015/16	26007
Safety & Security	2015/16	16378
Signals	2015/16	183371
Staff	2015/16	185085
Staff - Absence or Shortage	2015/16	102453
Staff Industrial Action	2015/16	622313
Stations	2015/16	43665
Track & Civils	2015/16	99962
Transplant Operations	2015/16	1679
Other	2015/16	551
Vandalism	2015/16	12400
Weather	2015/16	2736
TOTAL	2015/16	2035177
Animals / Pests	2016/17	1607
ATP / ATO	2016/17	18673
Bridge Strike	2016/17	78
Crowding	2016/17	27452
Customers & Public	2016/17	342329
External Properties	2016/17	4070
Fleet	2016/17	491012
Gas / Water / Sewage	2016/17	542
National Rail Operations	2016/17	33201
Other LU Operations	2016/17	4510
Power Failure	2016/17	16339
Safety & Security	2016/17	25420
Signals	2016/17	206255
Staff	2016/17	209413
Staff - Absence or Shortage	2016/17	250621
Staff Industrial Action	2016/17	187958
Stations	2016/17	58210
Track & Civils	2016/17	69383
Transplant Operations	2016/17	2008
Other	2016/17	235
Vandalism	2016/17	17970
Weather	2016/17	39150
TOTAL	2016/17	2006433
\.


--
-- Data for Name: lchbyline; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lchbyline (line, year, lost_customer_hours) FROM stdin;
Bakerloo	2004/05	138947
Central	2004/05	496082
Waterloo & City	2004/05	18935
Circle + H&C	2004/05	273311
District	2004/05	369788
Jubilee	2004/05	600094
Metropolitan	2004/05	180533
Northern	2004/05	626819
Piccadilly	2004/05	446001
Victoria	2004/05	299375
Bakerloo	2005/06	156058
Central	2005/06	485757
Waterloo & City	2005/06	29434
Circle + H&C	2005/06	626193
District	2005/06	637731
Jubilee	2005/06	608316
Metropolitan	2005/06	206128
Northern	2005/06	866307
Piccadilly	2005/06	880805
Victoria	2005/06	336887
Bakerloo	2006/07	145593
Central	2006/07	479671
Waterloo & City	2006/07	5843
Circle + H&C	2006/07	354001
District	2006/07	472908
Jubilee	2006/07	484972
Metropolitan	2006/07	188844
Northern	2006/07	508605
Piccadilly	2006/07	486127
Victoria	2006/07	386346
Bakerloo	2007/08	183043
Central	2007/08	625915
Waterloo & City	2007/08	16666
Circle + H&C	2007/08	437866
District	2007/08	510653
Jubilee	2007/08	581938
Metropolitan	2007/08	150866
Northern	2007/08	478547
Piccadilly	2007/08	435581
Victoria	2007/08	352604
Bakerloo	2008/09	134547
Central	2008/09	378720
Waterloo & City	2008/09	17313
Circle + H&C	2008/09	388706
District	2008/09	391038
Jubilee	2008/09	567377
Metropolitan	2008/09	122895
Northern	2008/09	307662
Piccadilly	2008/09	273543
Victoria	2008/09	234805
Bakerloo	2009/10	122391
Central	2009/10	417906
Waterloo & City	2009/10	16859
Circle + H&C	2009/10	314117
District	2009/10	271056
Jubilee	2009/10	464464
Metropolitan	2009/10	136101
Northern	2009/10	268515
Piccadilly	2009/10	275521
Victoria	2009/10	260487
Bakerloo	2010/11	132692
Central	2010/11	438268
Waterloo & City	2010/11	17622
Circle + H&C	2010/11	267328
District	2010/11	362412
Jubilee	2010/11	640937
Metropolitan	2010/11	192324
Northern	2010/11	297321
Piccadilly	2010/11	323690
Victoria	2010/11	369435
Bakerloo	2011/12	84327
Central	2011/12	321259
Waterloo & City	2011/12	8836
Circle + H&C	2011/12	149762
District	2011/12	232091
Jubilee	2011/12	538108
Metropolitan	2011/12	139563
Northern	2011/12	207759
Piccadilly	2011/12	243172
Victoria	2011/12	267520
Bakerloo	2012/13	128419
Central	2012/13	303719
Waterloo & City	2012/13	7228
Circle + H&C	2012/13	146285
District	2012/13	229788
Jubilee	2012/13	347611
Metropolitan	2012/13	124437
Northern	2012/13	157581
Piccadilly	2012/13	156745
Victoria	2012/13	156455
Bakerloo	2013/14	79786
Central	2013/14	339225
Waterloo & City	2013/14	12831
Circle + H&C	2013/14	194924
District	2013/14	197556
Jubilee	2013/14	338750
Metropolitan	2013/14	116044
Northern	2013/14	191029
Piccadilly	2013/14	189575
Victoria	2013/14	203457
Bakerloo	2014/15	72633
Central	2014/15	410197
Waterloo & City	2014/15	12290
Circle + H&C	2014/15	165919
District	2014/15	222224
Jubilee	2014/15	292024
Metropolitan	2014/15	94278
Northern	2014/15	139362
Piccadilly	2014/15	205068
Victoria	2014/15	129217
Bakerloo	2015/16	77603
Central	2015/16	442162
Waterloo & City	2015/16	11809
Circle + H&C	2015/16	203759
District	2015/16	254144
Jubilee	2015/16	312132
Metropolitan	2015/16	103054
Northern	2015/16	204115
Piccadilly	2015/16	282150
Victoria	2015/16	144248
Bakerloo	2016/17	98363
Central	2016/17	426400
Waterloo & City	2016/17	12605
Circle + H&C	2016/17	233986
District	2016/17	208111
Jubilee	2016/17	223664
Metropolitan	2016/17	81367
Northern	2016/17	155719
Piccadilly	2016/17	420445
Victoria	2016/17	145774
\.


--
-- Data for Name: schedule_operated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule_operated (line, year, schedule_operated) FROM stdin;
Central	2004/05	96.20
Waterloo & City	2004/05	96.50
Circle & Ham	2004/05	92.90
District	2004/05	96.60
Jubilee	2004/05	96.90
Metropolitan	2004/05	96.20
Northern	2004/05	93.50
Piccadilly	2004/05	94.20
Victoria	2004/05	96.50
TOTAL ALL LINES	2004/05	95.30
Central	2005/06	97.10
Waterloo & City	2005/06	96.50
Circle & Ham	2005/06	85.10
District	2005/06	93.10
Jubilee	2005/06	96.50
Metropolitan	2005/06	96.50
Northern	2005/06	90.60
Piccadilly	2005/06	90.80
Victoria	2005/06	96.50
TOTAL ALL LINES	2005/06	93.50
Central	2006/07	96.80
Waterloo & City	2006/07	97.70
Circle & Ham	2006/07	90.10
District	2006/07	95.40
Jubilee	2006/07	96.60
Metropolitan	2006/07	95.80
Northern	2006/07	90.60
Piccadilly	2006/07	93.60
Victoria	2006/07	96.40
TOTAL ALL LINES	2006/07	94.50
Central	2007/08	95.50
Waterloo & City	2007/08	95.50
Circle & Ham	2007/08	87.50
District	2007/08	95.60
Jubilee	2007/08	94.80
Metropolitan	2007/08	96.50
Northern	2007/08	95.80
Piccadilly	2007/08	93.20
Victoria	2007/08	96.00
TOTAL ALL LINES	2007/08	94.80
Central	2008/09	96.90
Waterloo & City	2008/09	93.50
Circle & Ham	2008/09	88.90
District	2008/09	96.60
Jubilee	2008/09	94.90
Metropolitan	2008/09	96.90
Northern	2008/09	98.20
Piccadilly	2008/09	96.70
Victoria	2008/09	97.80
TOTAL ALL LINES	2008/09	96.40
Central	2009/10	97.50
Waterloo & City	2009/10	95.20
Circle & Ham	2009/10	90.80
District	2009/10	97.50
Jubilee	2009/10	95.50
Metropolitan	2009/10	96.50
Northern	2009/10	98.10
Piccadilly	2009/10	96.10
Victoria	2009/10	96.50
TOTAL ALL LINES	2009/10	96.60
Central	2010/11	96.30
Waterloo & City	2010/11	95.80
Circle & Ham	2010/11	92.00
District	2010/11	95.90
Jubilee	2010/11	93.70
Metropolitan	2010/11	93.80
Northern	2010/11	97.40
Piccadilly	2010/11	95.70
Victoria	2010/11	95.70
TOTAL ALL LINES	2010/11	95.60
Central	2011/12	96.70
Waterloo & City	2011/12	98.00
Circle & Ham	2011/12	94.60
District	2011/12	97.70
Jubilee	2011/12	96.50
Metropolitan	2011/12	96.20
Northern	2011/12	98.60
Piccadilly	2011/12	96.40
Victoria	2011/12	97.10
TOTAL ALL LINES	2011/12	97.00
Central	2012/13	97.60
Waterloo & City	2012/13	98.30
Circle & Ham	2012/13	95.00
District	2012/13	97.70
Jubilee	2012/13	97.70
Metropolitan	2012/13	96.70
Northern	2012/13	98.70
Piccadilly	2012/13	97.90
Victoria	2012/13	98.40
TOTAL ALL LINES	2012/13	97.60
Central	2013/14	97.20
Waterloo & City	2013/14	97.50
Circle & Ham	2013/14	94.90
District	2013/14	97.80
Jubilee	2013/14	97.80
Metropolitan	2013/14	97.30
Northern	2013/14	98.60
Piccadilly	2013/14	97.20
Victoria	2013/14	97.40
TOTAL ALL LINES	2013/14	97.50
Central	2014/15	96.30
Waterloo & City	2014/15	97.60
Circle & Ham	2014/15	95.90
District	2014/15	97.60
Jubilee	2014/15	98.00
Metropolitan	2014/15	97.80
Northern	2014/15	98.90
Piccadilly	2014/15	97.00
Victoria	2014/15	98.10
TOTAL ALL LINES	2014/15	97.60
Central	2015/16	96.00
Waterloo & City	2015/16	97.60
Circle & Ham	2015/16	94.60
District	2015/16	97.20
Jubilee	2015/16	98.00
Metropolitan	2015/16	97.50
Northern	2015/16	98.40
Piccadilly	2015/16	95.60
Victoria	2015/16	98.20
TOTAL ALL LINES	2015/16	97.10
Central	2016/17	96.20
Waterloo & City	2016/17	97.60
Circle & Ham	2016/17	93.20
District	2016/17	97.60
Jubilee	2016/17	98.60
Metropolitan	2016/17	97.80
Northern	2016/17	98.90
Piccadilly	2016/17	93.40
Victoria	2016/17	98.00
TOTAL ALL LINES	2016/17	96.90
Central	Unnamed: 14	NaN
Waterloo & City	Unnamed: 14	NaN
Circle & Ham	Unnamed: 14	NaN
District	Unnamed: 14	NaN
Jubilee	Unnamed: 14	NaN
Metropolitan	Unnamed: 14	NaN
Northern	Unnamed: 14	NaN
Piccadilly	Unnamed: 14	NaN
Victoria	Unnamed: 14	NaN
TOTAL ALL LINES	Unnamed: 14	NaN
Central	Unnamed: 15	NaN
Waterloo & City	Unnamed: 15	NaN
Circle & Ham	Unnamed: 15	NaN
District	Unnamed: 15	NaN
Jubilee	Unnamed: 15	NaN
Metropolitan	Unnamed: 15	NaN
Northern	Unnamed: 15	NaN
Piccadilly	Unnamed: 15	NaN
Victoria	Unnamed: 15	NaN
TOTAL ALL LINES	Unnamed: 15	NaN
Central	Unnamed: 16	NaN
Waterloo & City	Unnamed: 16	NaN
Circle & Ham	Unnamed: 16	NaN
District	Unnamed: 16	NaN
Jubilee	Unnamed: 16	NaN
Metropolitan	Unnamed: 16	NaN
Northern	Unnamed: 16	NaN
Piccadilly	Unnamed: 16	NaN
Victoria	Unnamed: 16	NaN
TOTAL ALL LINES	Unnamed: 16	NaN
Central	Unnamed: 17	NaN
Waterloo & City	Unnamed: 17	NaN
Circle & Ham	Unnamed: 17	NaN
District	Unnamed: 17	NaN
Jubilee	Unnamed: 17	NaN
Metropolitan	Unnamed: 17	NaN
Northern	Unnamed: 17	NaN
Piccadilly	Unnamed: 17	NaN
Victoria	Unnamed: 17	NaN
TOTAL ALL LINES	Unnamed: 17	NaN
Central	Unnamed: 18	NaN
Waterloo & City	Unnamed: 18	NaN
Circle & Ham	Unnamed: 18	NaN
District	Unnamed: 18	NaN
Jubilee	Unnamed: 18	NaN
Metropolitan	Unnamed: 18	NaN
Northern	Unnamed: 18	NaN
Piccadilly	Unnamed: 18	NaN
Victoria	Unnamed: 18	NaN
TOTAL ALL LINES	Unnamed: 18	NaN
Central	Unnamed: 19	NaN
Waterloo & City	Unnamed: 19	NaN
Circle & Ham	Unnamed: 19	NaN
District	Unnamed: 19	NaN
Jubilee	Unnamed: 19	NaN
Metropolitan	Unnamed: 19	NaN
Northern	Unnamed: 19	NaN
Piccadilly	Unnamed: 19	NaN
Victoria	Unnamed: 19	NaN
TOTAL ALL LINES	Unnamed: 19	NaN
\.


--
-- Name: css css_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.css
    ADD CONSTRAINT css_pkey PRIMARY KEY (line, year);


--
-- Name: esc_avl esc_avl_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.esc_avl
    ADD CONSTRAINT esc_avl_pkey PRIMARY KEY (line, year);


--
-- Name: excess_journey_time excess_journey_time_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.excess_journey_time
    ADD CONSTRAINT excess_journey_time_pkey PRIMARY KEY (line, year);


--
-- Name: lchbycategory lchbycategory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lchbycategory
    ADD CONSTRAINT lchbycategory_pkey PRIMARY KEY (category, year);


--
-- Name: lchbyline lchbyline_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lchbyline
    ADD CONSTRAINT lchbyline_pkey PRIMARY KEY (line, year);


--
-- PostgreSQL database dump complete
--

\unrestrict awQyxoxbjlXOM3IhkgZszVYRUsxIQ2l5osOvNTSiiAHHhPZ0IpcqwOTKq944Vbl

