import { useEffect, useState } from 'react'
import { AWARDS, GALLERY_IMAGES, REVIEWS } from '../data/restaurant'
import './Gallery.css'

export default function Gallery() {
  const [activeImage, setActiveImage] = useState(null)

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setActiveImage(null)
      }
    }

    if (activeImage) {
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', handleKeyDown)
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [activeImage])

  return (
    <>
      <section className="page-hero page-hero--tall">
        <img src="/images/gallery-cafe-interior.webp" alt="Café Fausse gallery" />
        <div className="page-hero-content">
          <p className="eyebrow">Visual Journey</p>
          <h1>Gallery</h1>
          <p className="hero-lead">Explore our ambiance, cuisine, and celebrated moments.</p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="gallery-grid">
            {GALLERY_IMAGES.map((image) => (
              <button
                key={image.src}
                type="button"
                className="gallery-item"
                onClick={() => setActiveImage(image)}
                aria-label={`View ${image.caption}`}
              >
                <img src={image.src} alt={image.alt} loading="lazy" />
                <span>{image.caption}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="section gallery-highlights">
        <div className="container highlights-grid">
          <div className="card card-luxury">
            <h2 className="section-title">Awards</h2>
            <ul>
              {AWARDS.map((award) => (
                <li key={award}>{award}</li>
              ))}
            </ul>
          </div>
          <div className="card card-luxury">
            <h2 className="section-title">Customer Reviews</h2>
            {REVIEWS.map((review) => (
              <blockquote key={review.source} className="gallery-review">
                <p>&ldquo;{review.quote}&rdquo;</p>
                <cite>&mdash; {review.source}</cite>
              </blockquote>
            ))}
          </div>
        </div>
      </section>

      {activeImage && (
        <div
          className="lightbox"
          role="dialog"
          aria-modal="true"
          aria-label={activeImage.caption}
          onClick={() => setActiveImage(null)}
        >
          <div className="lightbox-content" onClick={(event) => event.stopPropagation()}>
            <button
              type="button"
              className="lightbox-close"
              onClick={() => setActiveImage(null)}
              aria-label="Close image viewer"
            >
              &times;
            </button>
            <img src={activeImage.src} alt={activeImage.alt} />
            <p>{activeImage.caption}</p>
          </div>
        </div>
      )}
    </>
  )
}
