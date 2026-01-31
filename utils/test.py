from selenium.webdriver.common.action_chains import ActionChains

async def move_piece(driver, el1, el2):
    # 高亮
    driver.execute_script("arguments[0].style.border=\"3px solid red\";", el1)
    driver.execute_script("arguments[0].style.border=\"3px solid red\";", el2)
    
    # 拖动
    start_rect = el1.rect
    end_rect = el2.rect
    start_x = int(start_rect["x"] + start_rect["width"] / 2)
    start_y = int(start_rect["y"] + start_rect["height"] / 2)
    end_x = int(end_rect["x"] + end_rect["width"] / 2)
    end_y = int(end_rect["y"] + end_rect["height"] / 2)
    
    actions = ActionChains(driver)
    (actions.move_by_offset(start_x, start_y)
            .click()
            .move_by_offset(end_x - start_x, end_y - start_y)
            .click()
            .perform())
    
    # 移除高亮
    driver.execute_script("arguments[0].style.border=\"\";", el1)
    driver.execute_script("arguments[0].style.border=\"\";", el2)
