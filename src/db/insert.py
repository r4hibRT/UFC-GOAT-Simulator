from src.db.connection import get_connection

def insert_fighter(url, name, dob=None, height=None, reach=None, weight_class=None, stance=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO fighters (url, name, dob, height, reach, weight_class, stance)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
        RETURNING id;
    """, (url, name, dob, height, reach, weight_class, stance))

    row = cur.fetchone()

    if row is None:
        cur.execute("SELECT id FROM fighters WHERE url = %s;", (url,))
        row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()
    return row[0]


def insert_bout(date, fighter_a_id, fighter_b_id, winner_id, method, method_detail,
                round_, time, is_title_fight, is_defence):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bouts (date, fighter_a_id, fighter_b_id, winner_id, method, method_detail,
                           round, time, is_title_fight, is_defence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (date, fighter_a_id, fighter_b_id, winner_id, method, method_detail,
          round_, time, is_title_fight, is_defence))

    bout_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return bout_id


def insert_bout_stats(bout_id, fighter_id, stats):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bout_stats (bout_id, fighter_id, sig_strikes_landed, sig_strikes_attempted,
                                total_strikes_landed, total_strikes_attempted, takedowns_landed,
                                takedowns_attempted, submission_attempts, knockdowns, control_time_seconds)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        bout_id,
        fighter_id,
        stats["sig_strikes_landed"],
        stats["sig_strikes_attempted"],
        stats["total_strikes_landed"],
        stats["total_strikes_attempted"],
        stats["takedowns_landed"],
        stats["takedowns_attempted"],
        stats["submission_attempts"],
        stats["knockdowns"],
        stats["control_time_seconds"]
    ))

    conn.commit()
    cur.close()
    conn.close()