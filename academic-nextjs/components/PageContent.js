import { useSpring, animated } from 'react-spring'
import styles from './PageContent.module.css'

export default function PageContent({ children, isFlipping }) {
  const springProps = useSpring({
    transform: isFlipping
      ? 'perspective(1000px) rotateY(-15deg)'
      : 'perspective(1000px) rotateY(0deg)',
    opacity: isFlipping ? 0.8 : 1,
    config: {
      tension: 300,
      friction: 30,
    },
  })

  return (
    <div className={styles.pageContainer}>
      <animated.div
        className={styles.page}
        style={springProps}
      >
        <div className={styles.pageContent}>
          {children}
        </div>

        {/* Page curl effect overlay */}
        {isFlipping && (
          <div className={styles.pageCurl}>
            <div className={styles.curlShadow}></div>
          </div>
        )}
      </animated.div>
    </div>
  )
}
