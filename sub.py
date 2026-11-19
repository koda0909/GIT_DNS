import psycopg
from psycopg.rows import dict_row

# DSN : Data Source Name
DSN = "host=localhost port=5432 dbname=sportscenter user=postgres password=admin1234"

MONTH = "2026-11"

LIST_SQL = """
SELECT DISTINCT c.course_id, s.sport_name, c.course_name, c.class_days, c.fee
FROM courses c
JOIN sports s ON c.sport_id = s.sport_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
                        AND e.enroll_month = %s
ORDER BY c.course_id
"""

# 수강 신청가능 목록 조회
def list_courses(conn):
    for c in conn.execute(LIST_SQL, (MONTH,)):
        print(f"{c['course_id']:>3} | {c['sport_name']} | {c['course_name']} | {c['class_days']} | {c['fee']:,}원")

# 강좌명 검색 기능
def search_courses(conn):
    keyword = input("검색할 강좌명을 입력하세요: ")

    rows = conn.execute("""
        SELECT course_id, course_name, class_days, fee
        FROM courses
        WHERE course_name LIKE %s
        ORDER BY course_id
    """, (f"%{keyword}%",)).fetchall()

    if not rows:
        print("검색 결과가 없습니다.")
        return

    print("\n===== 강좌 검색 결과 =====")
    for row in rows:
        print(
            f"ID: {row['course_id']} | "
            f"강좌명: {row['course_name']} | "
            f"요일: {row['class_days']} | "
            f"수강료: {row['fee']:,}원"
        )

# 회원 전체 목록 조회
def list_members(conn):
    rows = conn.execute("""
        SELECT member_id, name, gender, phone
        FROM members
        ORDER BY member_id
    """).fetchall()

    print("\n===== 회원 목록 =====")

    for row in rows:
        print(
            f"ID: {row['member_id']} | "
            f"이름: {row['name']} | "
            f"성별: {row['gender']} | "
            f"전화번호: {row['phone']}"
        )


# 회원 이름으로 회원 ID 조회
def find_member_id(conn):
    name = input("회원 이름을 입력하세요: ")

# 회원 이름으로 회원 ID 조회
def find_member_id(conn):
    name = input("회원 이름을 입력하세요: ")

    row = conn.execute(
        "SELECT member_id FROM members WHERE name = %s",
        (name,)
    ).fetchone()

    if row is None:
        print("해당 회원을 찾을 수 없습니다.")
        return None

    print(f"회원 ID: {row['member_id']}")
    return row['member_id']


# TODO: 입력 로직 구현
MEMBER_ID = 10
COURSE_ID = 1

# 수강 신청
def enroll(conn, member_id, course_id):
    # 신청한 강좌의 수강료 조회
    row = conn.execute(
        "SELECT fee FROM courses WHERE course_id = %s",
        (course_id,)
    ).fetchone()

    if row is None:
        print("존재하지 않는 강좌입니다.")
        return

    # 조회한 수강료를 fee 변수에 저장
    fee = row['fee']

    conn.execute(
        "INSERT INTO enrollments (member_id, course_id, enroll_month, status, pay_amount) "
        "VALUES (%s, %s, %s, '수강중', %s)",
        (member_id, course_id, MONTH, fee)
    )
    print(f"수강신청 완료되었습니다. 수강료: {fee:,}원")

def main():
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        # 수강 목록
        list_courses(conn)

        # 강좌명 검색
        search_courses(conn)

        # 회원 목록
        list_members(conn)

        # 회원 이름으로 회원 ID 조회
        MEMBER_ID = find_member_id(conn)

        if MEMBER_ID is None:
            return

        # 수강 신청
        enroll(conn, MEMBER_ID, COURSE_ID)

        # row = conn.execute("SELECT current_database(), current_user").fetchone()
        # print("연결 성공:", row)
        # rows = conn.execute("SELECT course_id, course_name, fee FROM courses LIMIT 5").fetchall()
        # for row in rows:
        #     print(row["course_name"], row["fee"])

if __name__ == "__main__":
    main()
