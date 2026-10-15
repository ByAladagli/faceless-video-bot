"""Browser-based uploads for creator-owned accounts; no platform API is used.

The browser profile is persistent. Sign in manually the first time, then rerun.
Selectors and flows can change when platforms update their UI; failures are
reported as failures and are never silently marked as published.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parent
PROFILE_ROOT = Path(os.getenv("SELENIUM_PROFILE_DIR", str(ROOT / "browser_profiles"))).resolve()
HEADLESS = os.getenv("SELENIUM_HEADLESS", "0").strip().lower() in {"1", "true", "yes"}
WAIT_SECONDS = int(os.getenv("SELENIUM_WAIT_SECONDS", "25"))


class PublishError(RuntimeError):
    pass


def _driver(platform: str):
    PROFILE_ROOT.mkdir(parents=True, exist_ok=True)
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_ROOT / platform}")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    if HEADLESS:
        options.add_argument("--headless=new")
    try:
        return webdriver.Chrome(options=options)
    except WebDriverException as exc:
        raise PublishError(
            "Chrome/ChromeDriver başlatılamadı. Google Chrome kurulu olmalı; "
            "ilk çalıştırmada görünür tarayıcıyla oturum açın. "
            f"Ayrıntı: {exc}"
        ) from exc


def _wait(driver, condition, timeout=WAIT_SECONDS):
    return WebDriverWait(driver, timeout).until(condition)


def _click_text(driver, candidates: list[str], timeout=WAIT_SECONDS):
    """Click a visible button or element whose visible text matches a candidate."""
    end = time.time() + timeout
    last_error = None
    while time.time() < end:
        for candidate in candidates:
            xpath = (
                "//*[self::button or self::div[@role='button'] or self::span]"
                "[normalize-space(.)=" + repr(candidate) + "]"
            )
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        driver.execute_script("arguments[0].click();", element)
                        return element
            except WebDriverException as exc:
                last_error = exc
        time.sleep(0.4)
    raise PublishError(
        f"Arayüzde beklenen düğme bulunamadı: {candidates}. "
        "Platform arayüzü değişmiş veya oturum açılmamış olabilir."
    ) from last_error


def _file_input(driver, video_path: Path):
    element = _wait(driver, EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    element.send_keys(str(video_path.resolve()))
    return element


def _fill_first(driver, selectors: list[tuple[str, str]], value: str, label: str):
    last_error = None
    for by, selector in selectors:
        try:
            element = _wait(driver, EC.presence_of_element_located((by, selector)), timeout=5)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            element.click()
            # Contenteditable elements and standard inputs both accept clear/send_keys.
            try:
                element.clear()
            except WebDriverException:
                pass
            element.send_keys(value)
            return element
        except Exception as exc:
            last_error = exc
    raise PublishError(f"{label} alanı bulunamadı veya doldurulamadı.") from last_error


def _verify_visible(driver, phrases: list[str], timeout=WAIT_SECONDS):
    end = time.time() + timeout
    while time.time() < end:
        body = (driver.find_element(By.TAG_NAME, "body").text or "").casefold()
        if any(phrase.casefold() in body for phrase in phrases):
            return True
        time.sleep(0.5)
    return False


def publish_youtube(video_path: Path, title: str, description: str) -> dict:
    driver = _driver("youtube")
    try:
        driver.get("https://studio.youtube.com/")
        if "accounts.google.com" in driver.current_url:
            raise PublishError("YouTube oturumu açık değil. Tarayıcıda manuel giriş yapıp tekrar çalıştırın.")
        _click_text(driver, ["Create", "Oluştur"])
        _click_text(driver, ["Upload videos", "Video yükle"])
        _file_input(driver, video_path)
        _fill_first(driver, [
            (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='title' i]"),
            (By.CSS_SELECTOR, "#title-textarea [contenteditable='true']"),
        ], title[:100], "YouTube başlık")
        _fill_first(driver, [
            (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='description' i]"),
            (By.CSS_SELECTOR, "#description-textarea [contenteditable='true']"),
        ], description[:5000], "YouTube açıklama")
        # Audience choice is required by the Studio upload wizard.
        _click_text(driver, ["No, it's not made for kids", "Hayır, çocuklara özel değil"])
        for _ in range(3):
            try:
                _click_text(driver, ["Next", "İleri"], timeout=5)
            except PublishError:
                break
        # Publish publicly now; platform may show an additional confirmation step.
        _click_text(driver, ["Public", "Herkese açık"], timeout=8)
        _click_text(driver, ["Publish", "Yayınla"], timeout=8)
        if not _verify_visible(driver, ["Video published", "Video yayınlandı", "Publishing", "Yükleniyor"], timeout=40):
            raise PublishError("YouTube arayüzünde yayın/yükleme onayı doğrulanamadı.")
        return {"platform": "youtube", "status": "submitted", "url": driver.current_url}
    except TimeoutException as exc:
        raise PublishError("YouTube yüklemesi zaman aşımına uğradı; yayın doğrulanamadı.") from exc
    finally:
        driver.quit()


def publish_tiktok(video_path: Path, title: str, description: str) -> dict:
    driver = _driver("tiktok")
    try:
        driver.get("https://www.tiktok.com/tiktokstudio/upload")
        if "login" in driver.current_url.casefold():
            raise PublishError("TikTok oturumu açık değil. Tarayıcıda manuel giriş yapıp tekrar çalıştırın.")
        _file_input(driver, video_path)
        caption = (title.strip() + "\n\n" + description.strip())[:2200]
        _fill_first(driver, [
            (By.CSS_SELECTOR, "div[contenteditable='true'][data-text='true']"),
            (By.CSS_SELECTOR, "div[contenteditable='true']"),
            (By.CSS_SELECTOR, "textarea"),
        ], caption, "TikTok açıklama")
        _click_text(driver, ["Post", "Publish", "Paylaş", "Yayınla"], timeout=30)
        if not _verify_visible(driver, ["uploaded", "posted", "published", "yükleme tamamlandı", "paylaşıldı"], timeout=45):
            raise PublishError("TikTok arayüzünde yayın onayı doğrulanamadı.")
        return {"platform": "tiktok", "status": "submitted", "url": driver.current_url}
    except TimeoutException as exc:
        raise PublishError("TikTok yüklemesi zaman aşımına uğradı; yayın doğrulanamadı.") from exc
    finally:
        driver.quit()


def publish_instagram(video_path: Path, title: str, description: str) -> dict:
    driver = _driver("instagram")
    try:
        driver.get("https://www.instagram.com/")
        if "/accounts/login" in driver.current_url:
            raise PublishError("Instagram oturumu açık değil. Tarayıcıda manuel giriş yapıp tekrar çalıştırın.")
        # Desktop web Reels upload UI availability varies by account/region.
        _click_text(driver, ["Create", "Oluştur"], timeout=12)
        _click_text(driver, ["Post", "Gönderi", "Reel", "Reels"], timeout=12)
        _file_input(driver, video_path)
        for text in ["Next", "İleri"]:
            try:
                _click_text(driver, [text], timeout=5)
            except PublishError:
                pass
        caption = (title.strip() + "\n\n" + description.strip())[:2200]
        _fill_first(driver, [
            (By.CSS_SELECTOR, "textarea[aria-label*='caption' i]"),
            (By.CSS_SELECTOR, "textarea[aria-label*='açıklama' i]"),
            (By.CSS_SELECTOR, "div[contenteditable='true']"),
        ], caption, "Instagram açıklama")
        _click_text(driver, ["Share", "Paylaş"], timeout=15)
        if not _verify_visible(driver, ["Your reel has been shared", "Gönderin paylaşıldı", "Reel paylaşıldı", "Shared"], timeout=45):
            raise PublishError("Instagram arayüzünde paylaşım onayı doğrulanamadı.")
        return {"platform": "instagram", "status": "submitted", "url": driver.current_url}
    except TimeoutException as exc:
        raise PublishError("Instagram yüklemesi zaman aşımına uğradı; yayın doğrulanamadı.") from exc
    finally:
        driver.quit()


PUBLISHERS: dict[str, Callable[[Path, str, str], dict]] = {
    "youtube": publish_youtube,
    "tiktok": publish_tiktok,
    "instagram": publish_instagram,
}


def publish(platform: str, video_path: str | Path, title: str, description: str) -> dict:
    key = platform.strip().lower()
    if key not in PUBLISHERS:
        raise ValueError(f"Desteklenmeyen platform: {platform}")
    path = Path(video_path).resolve()
    if not path.is_file() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"Video dosyası bulunamadı veya boş: {path}")
    return PUBLISHERS[key](path, title, description)
