'use strict';

/*
 * Renvoie les écrans tactiles sans souris (téléphone, tablette) vers unsupported.html.
 *
 * Chargé en premier par chaque page de contenu. Un ordinateur, même à écran tactile,
 * garde l'accès : son pointeur principal est fin et il sait survoler. Sans `matchMedia`,
 * la page reste accessible.
 */

const TOUCH_ONLY_QUERY = '(pointer: coarse) and (hover: none)';

/** Ouvre unsupported.html à la place de la page quand l'écran est tactile sans souris. */
function redirectTouchOnlyScreen() {
  if (window.matchMedia?.(TOUCH_ONLY_QUERY).matches) {
    window.location.replace('unsupported.html');
  }
}

redirectTouchOnlyScreen();
