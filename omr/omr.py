import argparse
import cv2
import numpy as np

import os

# When the four corners are identified, we will do a four-point
# perspective transform such that the outmost points of each
# corner map to a TRANSF_SIZE x TRANSF_SIZE square image.
TRANSF_SIZE = 512*4

#
# Answer sheet properties.
#

K = 4
ANSWER_SHEET_WIDTH = 689*K   # proporcional a 2100, NO cambiar
ANSWER_SHEET_HEIGHT = 1039*K # proporcional a 2970, NO cambiar

ANSWER_PATCH_HEIGHT = 10*K
ANSWER_PATCH_HEIGHT_WITH_MARGIN = 37.8*K

COLUMN_WIDTH_WITH_MARGIN = 250.8*K

ANSWER_PATCH_LEFT_MARGIN = [
    53.3*K,
    53.3*K + 1 * COLUMN_WIDTH_WITH_MARGIN,
    53.3*K + 2 * COLUMN_WIDTH_WITH_MARGIN
    ]

ANSWER_PATCH_RIGHT_MARGIN = [
    530*K,
    530*K - 1 * COLUMN_WIDTH_WITH_MARGIN,
    530*K - 2 * COLUMN_WIDTH_WITH_MARGIN
    ]

FIRST_ANSWER_PATCH_TOP_Y = [
    475*K,
    475*K,
    475*K
    ]

ACCUMULATED_QUESTIONS =  [
    15,
    30,
    45,
    ]

N_QUESTIONS = ACCUMULATED_QUESTIONS[-1]

ALTERNATIVE_HEIGHT = 11.5*K
ALTERNATIVE_WIDTH = 11.5*K
ALTERNATIVE_WIDTH_WITH_MARGIN = 22.3*K

#PARA EL DNI
NUMBER_TOP_Y = 207 * K # COORDENADA Y DE LA PRIMERA FILA DE NUMEROS( FILA  DE 0 )
NUMBER_HEIGHT_WITH_MARGIN = 19.1 * K
NUMBER_HEIGHT = 10.7 * K
NUMBER_WIDTH_WITH_MARGIN = 22.55 * K
NUMBER_WIDTH = K * 15
LAST_NUMBER_PATCH = 391 * K #COORDENADA Y DEl final del digito 9)
NUMBER_PATCH_LEFT_MARGIN = 236.0 * K # COMO LA DE LA RESPUESTA
N_NUMBERS = 8

#PARA EL MODELO
MODEL_TOP_Y = 379 * K
MODEL_LEFT_MARGIN = 531 * K
MODEL_HEIGHT = 11 * K
MODEL_WIDTH = 14 * K
MODEL_WIDTH_WITH_MARGIN = 23 * K
MODEL_NUMBER = 4

# PATHS ABSOLUTOS
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

CORNER1_NAME = 'img/etsit1.png'
CORNER1_PATH = os.path.join(CURRENT_PATH, CORNER1_NAME)

CORNER2_NAME = 'img/etsit2.png'
CORNER2_PATH = os.path.join(CURRENT_PATH, CORNER2_NAME)

def calculate_contour_features(contour):
    #print(cv2.contourArea(contour))
    moments = cv2.moments(contour)
    return cv2.HuMoments(moments)


def calculate_corner_features_superior():

    corner_img = cv2.imread(CORNER1_PATH)
    corner_img_gray = cv2.cvtColor(corner_img, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(
        corner_img_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) != 2:
        raise RuntimeError(
            'Did not find the expected contours when looking for the corner')

    corner_contour = next(ct
                          for i, ct in enumerate(contours)
                          if hierarchy[0][i][3] != -1)

    return calculate_contour_features(corner_contour)

def calculate_corner_features_inferior():

    corner_img = cv2.imread(CORNER2_PATH)
    corner_img_gray = cv2.cvtColor(corner_img, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(
        corner_img_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) != 2:
        raise RuntimeError(
            'Did not find the expected contours when looking for the corner')

    # Following our assumptions as stated above, we take the contour that has a parent
    # contour (that is, it is _not_ the outer contour) to be the corner contour.
    # If in trouble, verify that this contour is the corner contour with
    # cv2.drawContours(corner_img, [corner_contour], -1, (255, 0, 0))

    corner_contour = next(ct
                          for i, ct in enumerate(contours)
                          if hierarchy[0][i][3] != -1)


    return calculate_contour_features(corner_contour)

def normalize(im):

    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # Filter the grayscale image with a 3x3 kernel
    blurred = cv2.GaussianBlur(im_gray, (3, 3), 0)
    return cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 77, 10)


def get_approx_contour(contour, tol=.01):
    """Gets rid of 'useless' points in the contour."""
    epsilon = tol * cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, epsilon, True)

def get_contours(image_gray):
    contours, hierarchy = cv2.findContours(
        image_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return map(get_approx_contour, contours)

def get_contorno_superior(contours):

    corner_features = calculate_corner_features_superior()

    contornoFiltrado = filter(filtrar_contorno_superior, contours)

    return sorted(
        contornoFiltrado,
        key=lambda c: features_distance(
                corner_features,
                calculate_contour_features(c)))[:1]

def filtrar_contorno_superior(contour):
    return (cv2.contourArea(contour) > 100*500)

def get_contorno_inferior(contours):
    corner_features = calculate_corner_features_inferior()

    contornoFiltrado = filter(filtrar_contorno_inferior, contours)

    return sorted(
        contornoFiltrado,
        key=lambda c: features_distance(
                corner_features,
                calculate_contour_features(c)))[:1]

def filtrar_contorno_inferior(contour):
    return (cv2.contourArea(contour) > 500*500)

def get_bounding_rect(contour):
    #rect = cv2.minAreaRect(contour)
    #box = cv2.boxPoints(rect)
    #return np.int0(box)

    return(contour[:, 0, :])

def features_distance(f1, f2):
    return np.linalg.norm(np.array(f1) - np.array(f2))

def draw_point(point, img, radius=5, color=(0, 0, 255)):
    cv2.circle(img, tuple(point), radius, color, -1)

def get_centroid(contour):
    m = cv2.moments(contour)
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])
    return (x, y)

def sort_points_counter_clockwise(points):
    origin = np.mean(points, axis=0)

    def positive_angle(p):
        x, y = p - origin
        ang = np.arctan2(y, x)
        return 2 * np.pi + ang if ang < 0 else ang

    return sorted(points, key=positive_angle)

def get_outmost_points(contours):
    all_points = np.concatenate(contours)
    return get_bounding_rect(all_points)

def perspective_transform(img, points):
    source = np.array(
        points,
        dtype="float32")

    dest = np.array([
        [TRANSF_SIZE, TRANSF_SIZE],
        [0, TRANSF_SIZE],
        [0, 0],
        [TRANSF_SIZE, 0]],
        dtype="float32")

    transf = cv2.getPerspectiveTransform(source, dest)
    warped = cv2.warpPerspective(img, transf, (TRANSF_SIZE, TRANSF_SIZE))

    return warped

def sheet_coord_to_transf_coord(x, y):
    return list(map(lambda n: int(np.round(n)), (
        TRANSF_SIZE * x / ANSWER_SHEET_WIDTH,
        TRANSF_SIZE * y / ANSWER_SHEET_HEIGHT
    )))

def get_question_patch(transf, question_index):

    columna = 0
    while(int(question_index / ACCUMULATED_QUESTIONS[columna]) >= 1):
        columna = columna + 1

    question_index = question_index if columna == 0 else (question_index - ACCUMULATED_QUESTIONS[columna-1])

    # Top left of question patch q_number
    tl = sheet_coord_to_transf_coord(
        ANSWER_PATCH_LEFT_MARGIN[columna],
        FIRST_ANSWER_PATCH_TOP_Y[columna] + ANSWER_PATCH_HEIGHT_WITH_MARGIN * question_index
    )

    # Bottom right of question patch q_number
    br = sheet_coord_to_transf_coord(
        ANSWER_SHEET_WIDTH - ANSWER_PATCH_RIGHT_MARGIN[columna],
        FIRST_ANSWER_PATCH_TOP_Y[columna] +
        ANSWER_PATCH_HEIGHT +
        ANSWER_PATCH_HEIGHT_WITH_MARGIN * question_index
    )

    return transf[tl[1]:br[1], tl[0]:br[0]]


def get_question_patches(transf):
    for i in range(N_QUESTIONS):
        yield get_question_patch(transf, i)

def get_DNI_patch ( transf, number_index ):

    tl= sheet_coord_to_transf_coord(NUMBER_PATCH_LEFT_MARGIN + number_index * NUMBER_WIDTH_WITH_MARGIN,
                                        NUMBER_TOP_Y)
    br= sheet_coord_to_transf_coord(NUMBER_PATCH_LEFT_MARGIN + NUMBER_WIDTH + number_index * NUMBER_WIDTH_WITH_MARGIN,
                                         LAST_NUMBER_PATCH)

    return transf[tl[1]:br[1], tl[0]:br[0]]

def get_DNI_patches(transf):
    for i in range(N_NUMBERS):
        yield get_DNI_patch(transf,i)

def get_model_patch(transf):

    tl= sheet_coord_to_transf_coord(MODEL_LEFT_MARGIN ,MODEL_TOP_Y )
    br= sheet_coord_to_transf_coord(MODEL_LEFT_MARGIN + MODEL_WIDTH + 3*MODEL_WIDTH_WITH_MARGIN, MODEL_TOP_Y+ MODEL_HEIGHT)

    return transf[tl[1]:br[1], tl[0]:br[0]]


def get_numbers(index): # Comprobar orden
    return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"][index] if index is not None else "0"


def get_digit_patches(DNI_patch):
    for i in range(10):
        _, y0 = sheet_coord_to_transf_coord(0, NUMBER_HEIGHT_WITH_MARGIN * i)
        _, y1 = sheet_coord_to_transf_coord(0, NUMBER_HEIGHT +
                                            NUMBER_HEIGHT_WITH_MARGIN * i)

        yield DNI_patch[y0:y1, :]

def get_model_exam_patches(model_patch):
    for i in range(4):
        x0, _ = sheet_coord_to_transf_coord(MODEL_WIDTH_WITH_MARGIN * i, 0)
        x1, _ = sheet_coord_to_transf_coord(MODEL_WIDTH +
                                            MODEL_WIDTH_WITH_MARGIN * i, 0)
        yield model_patch[:, x0:x1]

def get_alternative_patches(question_patch):
    for i in range(5):
        x0, _ = sheet_coord_to_transf_coord(ALTERNATIVE_WIDTH_WITH_MARGIN * i, 0)
        x1, _ = sheet_coord_to_transf_coord(ALTERNATIVE_WIDTH +
                                            ALTERNATIVE_WIDTH_WITH_MARGIN * i, 0)
        yield question_patch[:, x0:x1]

def draw_marked_alternative(question_patch, index):
    cx, cy = sheet_coord_to_transf_coord(
        ALTERNATIVE_WIDTH * (2 * index + .5),
        ALTERNATIVE_HEIGHT / 2)
    draw_point((cx, cy), question_patch, radius=5, color=(0, 255, 0))

    cx1, cy1 = sheet_coord_to_transf_coord(
        ALTERNATIVE_WIDTH_WITH_MARGIN*index,
        0)

    cx2, cy2 = sheet_coord_to_transf_coord(
        ALTERNATIVE_WIDTH_WITH_MARGIN*index + ALTERNATIVE_WIDTH,
        ALTERNATIVE_HEIGHT)

    cv2.rectangle(question_patch, (cx1, cy1), (cx2, cy2), (255,0,0), 1)

def draw_marked_digit(DNI_patch, index):
    cx, cy = sheet_coord_to_transf_coord(
        NUMBER_WIDTH / 2,
        NUMBER_HEIGHT * .5 + NUMBER_HEIGHT_WITH_MARGIN * index)
    draw_point((cx, cy), DNI_patch, radius=5, color=(0, 255, 0))

    cx1, cy1 = sheet_coord_to_transf_coord(
        0,
        NUMBER_HEIGHT_WITH_MARGIN*index)

    cx2, cy2 = sheet_coord_to_transf_coord(
        NUMBER_WIDTH,
        NUMBER_HEIGHT_WITH_MARGIN*index + NUMBER_HEIGHT)

    cv2.rectangle(DNI_patch, (cx1, cy1), (cx2, cy2), (255,0,0), 1)

def draw_marked_version(version_patch, index):
    cx, cy = sheet_coord_to_transf_coord(
        MODEL_WIDTH * .5 + MODEL_WIDTH_WITH_MARGIN * index,
        MODEL_HEIGHT / 2)
    draw_point((cx, cy), version_patch, radius=5, color=(0, 255, 0))

    cx1, cy1 = sheet_coord_to_transf_coord(
        MODEL_WIDTH_WITH_MARGIN*index,
        0)

    cx2, cy2 = sheet_coord_to_transf_coord(
        MODEL_WIDTH_WITH_MARGIN*index + MODEL_WIDTH,
        MODEL_HEIGHT)

    cv2.rectangle(version_patch, (cx1, cy1), (cx2, cy2), (255,0,0), 1)

    cv2.imwrite("MARKED_VERSION" + str(index)+".jpg", version_patch)

def get_marked_alternative(alternative_patches):

    means = list(map(np.mean, alternative_patches))
    sorted_means = sorted(means)

    # Simple heuristic
    #print(sorted_means)
    if sorted_means[0]/sorted_means[1] > 0.8:
        return None

    return np.argmin(means)

def get_letter(alt_index):
    return ["A", "B", "C", "D", "E"][alt_index] if alt_index is not None else "N/A"

def sortPoints(point):
    return point[1]

def get_answers(source_file, dest_file):
    im_orig = cv2.imread(source_file)
    #im_orig = cv2.rotate(im_orig, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)

    im_normalized = normalize(im_orig)

    contours = get_contours(im_normalized)
    contours2 = get_contours(im_normalized)

    contorno_superior = get_contorno_superior(contours2)
    contorno_inferior = get_contorno_inferior(contours)

    outmost_superior = sort_points_counter_clockwise(get_outmost_points(contorno_superior))
    outmost_inferior = sort_points_counter_clockwise(get_outmost_points(contorno_inferior))
    outmost = [outmost_inferior[0], outmost_inferior[1], outmost_superior[2], outmost_superior[3]]

    color_transf = perspective_transform(im_orig, outmost)
    normalized_transf = perspective_transform(im_normalized, outmost)

    # Get answer array
    answers = []
    for i, q_patch in enumerate(get_question_patches(normalized_transf)):
        alt_index = get_marked_alternative(get_alternative_patches(q_patch))

        if alt_index is not None:
            question_patch = get_question_patch(color_transf, i)
            draw_marked_alternative(question_patch, alt_index)

        answers.append(get_letter(alt_index))

    # Get DNI array
    DNI = []
    for i, n_patch in enumerate(get_DNI_patches(normalized_transf)):
        alt_index = get_marked_alternative(get_digit_patches(n_patch))

        if alt_index is not None:
            DNI_patch = get_DNI_patch(color_transf, i)
            draw_marked_digit(DNI_patch, alt_index)

        DNI.append(get_numbers(alt_index))

    # Get version number
    model = 0
    m_patch = get_model_patch(normalized_transf)
    alt_index = get_marked_alternative(get_model_exam_patches((m_patch)))

    if alt_index is not None:
        version_patch = get_DNI_patch(color_transf, i)
        #draw_marked_version(version_patch, alt_index)

        if alt_index is not None:
            model = int(alt_index + 1)
        else:
            model = -1

    cv2.imwrite(dest_file, color_transf)

    #print(answers)

    return DNI, model, answers, color_transf
