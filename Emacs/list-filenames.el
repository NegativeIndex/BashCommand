;; I abandon the fancy modify-my-abbreviation function in the new version of lds
;; I also abandon my-lds-f functions


;; ;; 11/06/2011 version
;; (defun lds (pat)
;; "list file names in current directory"
;; (interactive "sFile names are ")
;; (setq patt (modify-my-abbreviation pat))
;; ;(princ (concat patt "\n")  (current-buffer))
;; (let (value)
;;  (setq ff (file-expand-wildcards patt))
;;  ; (princ ff (current-buffer))
;;  (let ((tss))
;;    (dolist (elt ff value)
;;      (setq tss elt)
;;      (setq value (concat  value ", " tss))))
;; (setq ss (substring value 2 nil))
;; (princ ss (current-buffer))
;; )
;; )



;; 05/25/2011 version
;; file name list
(defun fl (file-regular-expression)
  "list file names in current directory"
  (interactive "sFile names are ")
  (let ((file-names) (name-string))
    (setq file-names (file-expand-wildcards file-regular-expression))
    ;; (princ file-names (current-buffer))
    (let ((element))
      (dolist (element file-names name-string)
	(setq name-string (concat name-string ", \"" element "\""))))

    (setq ss (substring name-string 2 nil))
    (princ ss (current-buffer))
    )
  )


;; 05/25/2016 version with file name completion
;; file name completion
(defun fc ()
  "list file names in current directory"
  (interactive)
  (let ( (x (read-file-name "Enter file name:")) )
    ;; (princ x (current-buffer))
    ;; try to remove current directory name from x
    (setq ss (file-relative-name x "."))
    (setq ss (concat "\"" ss "\""))
    (princ ss  (current-buffer))

    
    )
  )
