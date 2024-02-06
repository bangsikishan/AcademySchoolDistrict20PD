import os
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.getcwd())
from utils import ( # noqa
    check_for_duplicate_amr_hash,
    create_database_session,
    generate_md5_hash,
    get_env_variables,
    initialize_webdriver,
    insert_to_amr_database,
)

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
env_path = os.path.join(script_directory, ".env")
[
    ecgains,
    _,
    base_url,
    executable_path,
    _,
    _,
    _,
    browser_type,
    smi_data_url,
    _,
    _,
    _,
    _,
    _
] = get_env_variables(env_path=env_path)

driver = initialize_webdriver(
    exec_path=executable_path,
    browser_type=browser_type,
    download_dir=None,
    is_headless=True,
)

db_session = create_database_session(database_url=smi_data_url)

driver.get(base_url)

wait = WebDriverWait(driver, 30)

try:
    parent_element = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "asd20-list__items"))
    )

    bid_elements = parent_element.find_elements(By.XPATH, "./*")

    for bid_element in bid_elements:
        link = bid_element.get_attribute("href")

        bid_id = bid_element.text[:15]
        bid_title = bid_element.text

        # BID NO + TITLE + DUE DATE
        hash = generate_md5_hash(ecgain=bid_id, bidno=bid_title, filename=None)

        if check_for_duplicate_amr_hash(session=db_session, hash=hash):
            continue
        
        insert_to_amr_database(
            session=db_session,
            ecgain=ecgains,
            number=bid_id,
            title=bid_title,
            due_date=None,
            hash=hash,
            url1=base_url,
            url2=link,
            description=bid_title,
        )
except Exception as e:
    print("[-] Exception thrown!")
    print(e)

driver.quit()
print(f"[+] End of script {script_path}!")