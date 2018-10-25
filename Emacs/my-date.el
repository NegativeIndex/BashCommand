;; This buffer is for notes you don't want to save, and for Lisp evaluation.
;; If you want to create a file, visit that file with C-x C-f,
;; then enter the text in that file's own buffer.


(defun my-date ()
  "insert the current date and time."
  (interactive)
  (setq ss (current-time-string))
  (setq year (substring ss 20 24))
  (setq day  (substring ss 8  10 ))
  (if (string= (substring day 0 1) " ") 
	(setq day (concat "0" (substring day 1 2))))
  (setq month (substring ss 4 7))
  (setq time (substring ss 11 19))

  (setq mm "00")
  (if (string-match "Jan"  month) (setq mm "01"))
  (if (string-match "Feb"  month) (setq mm "02"))
  (if (string-match "Mar"  month) (setq mm "03"))
  (if (string-match "Apr"  month) (setq mm "04"))
  (if (string-match "May"  month) (setq mm "05"))
  (if (string-match "Jun"  month) (setq mm "06"))
  (if (string-match "Jul"  month) (setq mm "07"))
  (if (string-match "Aug"  month) (setq mm "08"))
  (if (string-match "Sep"  month) (setq mm "09"))
  (if (string-match "Oct"  month) (setq mm "10"))
  (if (string-match "Nov"  month) (setq mm "11"))
  (if (string-match "Dec"  month) (setq mm "12"))  

  (setq bfix "***** ")
  (setq afix " *****\n")

  (setq output (concat bfix year "-" mm "-" day "   " time afix))

  (princ output (current-buffer)))
