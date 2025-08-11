from selenium import webdriver
import glob
import numpy as np
import matplotlib.pyplot as plt
import argparse

HES_WEBSITES = [
    "https://www.he-arc.ch/",
    "https://www.heig-vd.ch/",
    "https://www.hes-so.ch/",
    "https://www.heia-fr.ch/",
    "https://www.hesge.ch/",
]

DATA_FOLDER='./data'

def take_screenshot():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode for automation
    driver = webdriver.Firefox(options=options)

    for website in HES_WEBSITES:
        driver.get(website)
        screenshot_filename = f"{DATA_FOLDER}/screenshot_{website.split('.')[1]}.png"
        driver.save_screenshot(screenshot_filename)
        print(f"Screenshot saved as {screenshot_filename}")

    driver.quit()

def screenshot_analysis():
    images_paths = glob.glob(f"{DATA_FOLDER}/screenshot_*.png")
    images_colorfulness = np.zeros(len(images_paths))
    images_names = []
    for i,image_path in enumerate(images_paths):
        img = plt.imread(image_path)
        images_colorfulness[i] = image_colorfulness(img)
        images_names.append(image_path.split('screenshot_')[-1].split('.')[0])
    
    
    fig, ax = plt.subplots(figsize=(5,5))
    ax.barh(images_names, images_colorfulness, color='skyblue')
    ax.set_xlabel('Colorfulness')
    ax.set_ylabel('Website')
    ax.set_title('Colorfulness of HES Websites Screenshots')
    fig.tight_layout()
    plt.show()

def image_colorfulness(image):
    '''
    Compute "colorfulness" metric for an image.
    Based on Hasler and Süsstrunk's 2003 paper "Measuring Colorfulness in Natural Images".
    '''
    # split the image into its respective RGB components
    (B, G, R) = image[:, :, 2], image[:, :, 1], image[:, :, 0]
    # compute rg = R - G
    rg = np.absolute(R - G)
    # compute yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B)
    # compute the mean and standard deviation of both `rg` and `yb`
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    # combine the mean and standard deviations
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    # derive the "colorfulness" metric and return it
    return stdRoot + (0.3 * meanRoot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take screenshots of HES websites.")
    parser.add_argument("--update", action="store_true", help="Update screenshots")

    args = parser.parse_args()

    if args.update:
        take_screenshot()
    
    screenshot_analysis()

